# utils/recommender.py
# Contains all recommendation logic: scoring and filtering projects.

import math
import re
from collections import Counter

import json
import os

from utils.data_loader import load_all_projects

MAX_RESULTS = 3
MAX_RELATED = 3
_CLUSTERS_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "data",
    "clusters.json",
)

VALID_LEVELS = ["beginner", "intermediate", "advanced"]
VALID_TIME_AVAILABILITY = ["low", "medium", "high"]
VALID_INTERESTS = [
    "automation",
    "backend",
    "business logic",
    "cloud computing",
    "cybersecurity",
    "data",
    "devops",
    "education",
    "games",
    "machine learning/ai",
    "mobile",
    "productivity",
    "tools",
    "web",
]
SCORING_WEIGHTS = {
    "skill": 3,
    "level": 2,
    "interest": 2,
    "time": 1,
}

WEIGHT_SKILL = SCORING_WEIGHTS["skill"]
WEIGHT_LEVEL = SCORING_WEIGHTS["level"]
WEIGHT_INTEREST = SCORING_WEIGHTS["interest"]
WEIGHT_TIME = SCORING_WEIGHTS["time"]

# Common aliases and abbreviations for skills
# This improves recommendation accuracy by normalizing user input
SKILL_ALIASES = {
    "js": "javascript",
    "py": "python",
    "html5": "html",
    "css3": "css",
    "c++": "cpp",
    "web dev": "javascript",
}

def parse_skills(skills_string):
    """
    Convert a raw skills string into a normalized lowercase list.
    Accepts either a JSON array (e.g. '["Python","React"]') or a
    comma-separated string (e.g. "JS, HTML5, CSS3").

    Example:
        '["Python","React"]' -> ["python", "react"]
        "JS, HTML5, CSS3"   -> ["javascript", "html", "css"]
    """
    stripped = skills_string.strip()
    if stripped.startswith("["):
        try:
            parsed = json.loads(stripped)
            if isinstance(parsed, list):
                raw_skills = [str(s).strip().lower() for s in parsed if str(s).strip()]
                return [SKILL_ALIASES.get(skill, skill) for skill in raw_skills]
        except (json.JSONDecodeError, ValueError):
            pass
    raw_skills = [
        s.strip().lower()
        for s in skills_string.split(",")
        if s.strip()
    ]
    return [SKILL_ALIASES.get(skill, skill) for skill in raw_skills]

def _tokenize(text):
    return re.findall(r"[a-z0-9]+", str(text).lower())

def _project_text(project):
    parts = [
        project.get("title", ""),
        project.get("level", ""),
        project.get("interest", ""),
        project.get("time", ""),
        project.get("description", ""),
        " ".join(project.get("skills", [])),
        " ".join(project.get("tech_stack", [])),
        " ".join(project.get("features", [])),
    ]
    return " ".join(parts)

def _user_text(user_skills, level, interest, time_availability):
    return " ".join(user_skills + [level, interest, time_availability])

def _tf(tokens):
    counts = Counter(tokens)
    total = len(tokens) or 1
    return {token: count / total for token, count in counts.items()}

def _idf(documents):
    total_docs = len(documents)
    idf_scores = {}

    all_tokens = set(token for doc in documents for token in set(doc))

    for token in all_tokens:
        docs_with_token = sum(1 for doc in documents if token in doc)
        idf_scores[token] = math.log((1 + total_docs) / (1 + docs_with_token)) + 1

    return idf_scores

def _tfidf_vector(tokens, idf_scores):
    tf_scores = _tf(tokens)
    return {
        token: tf_scores[token] * idf_scores.get(token, 0)
        for token in tf_scores
    }

def _cosine_similarity(vec_a, vec_b):
    shared_tokens = set(vec_a) & set(vec_b)

    dot_product = sum(vec_a[token] * vec_b[token] for token in shared_tokens)
    magnitude_a = math.sqrt(sum(value ** 2 for value in vec_a.values()))
    magnitude_b = math.sqrt(sum(value ** 2 for value in vec_b.values()))

    if magnitude_a == 0 or magnitude_b == 0:
        return 0

    return dot_product / (magnitude_a * magnitude_b)

def ml_similarity_score(project, user_skills, level, interest, time_availability, all_projects):
    project_documents = [_tokenize(_project_text(p)) for p in all_projects]
    user_tokens = _tokenize(_user_text(user_skills, level, interest, time_availability))

    idf_scores = _idf(project_documents + [user_tokens])

    user_vector = _tfidf_vector(user_tokens, idf_scores)
    project_vector = _tfidf_vector(_tokenize(_project_text(project)), idf_scores)

    return _cosine_similarity(user_vector, project_vector)

def score_single_project(project, user_skills, level, interest, time_availability):
    TIME_RANKS = ["low", "medium", "high"]

    user_time    = time_availability.strip().lower()
    project_time = project.get("time", "").strip().lower()

    # If the project needs more time than the user has, exclude it.
    if project_time not in TIME_RANKS or user_time not in TIME_RANKS:
        return 0
    if TIME_RANKS.index(project_time) > TIME_RANKS.index(user_time):
        return 0

    score = 0

    # Compare user's skills against the project's required skills
    project_skills = [SKILL_ALIASES.get(s.lower(), s.lower()) for s in project.get("skills", [])]
    matched_skills = sum(1 for skill in user_skills if skill in project_skills)
    if project_skills:
        coverage = matched_skills / len(project_skills)
        score += matched_skills * SCORING_WEIGHTS["skill"] * coverage
    else:
        score += matched_skills * SCORING_WEIGHTS["skill"]

    level_match = False
    if project.get("level", "").lower() == level.lower():
        score += SCORING_WEIGHTS["level"]
        level_match = True

    interest_match = False
    p_interest = project.get("interest", "").lower()
    u_interest = interest.lower()
    # Use partial matching for interest as well
    if p_interest == u_interest or (u_interest and u_interest in p_interest) or (p_interest and p_interest in u_interest):
        score += SCORING_WEIGHTS["interest"]
        interest_match = True

    time_match = False
    if project.get("time", "").lower() == time_availability.lower():
        score += SCORING_WEIGHTS["time"]
        time_match = True

    graph = _load_skill_graph()
    score += gap_boost(user_skills, project_skills, graph)

    matched_skills_list = [skill for skill in user_skills if skill in project_skills]
    match_details = {
        "matched_skills": matched_skills_list,
        "level": level_match,
        "interest": interest_match,
        "time": time_match
    }

    return score, match_details

# ---------------------------------------------------------------------------
# Skill graph helpers
# ---------------------------------------------------------------------------

def _load_skill_graph():
    """Load skill_graph.json from data/. Returns empty dict on failure."""
    path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "data", "skill_graph.json"
    )
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def _hops_to_skill(target, user_skills, graph, max_hops=3):
    """
    BFS from every known user skill — find minimum hops to reach target.
    Returns None if unreachable within max_hops.
    """
    if target in user_skills:
        return 0

    visited = set(user_skills)
    frontier = list(user_skills)
    
    for hop in range(1, max_hops + 1):
        next_frontier = []
        for skill in frontier:
            for neighbour in graph.get(skill, []):
                if neighbour == target:
                    return hop
                if neighbour not in visited:
                    visited.add(neighbour)
                    next_frontier.append(neighbour)
        frontier = next_frontier

    return None


def gap_boost(user_skills, project_skills, graph):
    """
    For each project skill the user doesn't have,
    compute boost based on graph distance.
    
    boost = 1/hops per reachable missing skill
    Returns total boost score (float).
    """
    boost = 0.0
    for skill in project_skills:
        if skill not in user_skills:
            hops = _hops_to_skill(skill, user_skills, graph)
            if hops and hops > 0:
                boost += 1.0 / hops
    return round(boost, 3)


def get_progression(user_skills, recommended_ids, all_projects, graph):
    """
    Return projects that are 1 hop away from user's current skills
    but were NOT already recommended.
    """
    # Find all 1-hop reachable skills
    reachable = set()
    for skill in user_skills:
        for neighbour in graph.get(skill, []):
            reachable.add(neighbour)

    progression = []
    for project in all_projects:
        if project["id"] in recommended_ids:
            continue
        project_skills = [
            SKILL_ALIASES.get(s.lower(), s.lower())
            for s in project.get("skills", [])
        ]
        # Project skills must overlap with reachable skills
        if any(s in reachable for s in project_skills):
            boost = gap_boost(user_skills, project_skills, graph)
            progression.append({
                "project": project,
                "gap_score": boost
            })
            
    progression.sort(key=lambda x: x["gap_score"], reverse=True)
    return progression[:3]


# ---------------------------------------------------------------------------
# Clustering helpers
# ---------------------------------------------------------------------------

def _load_clusters():
    """
    Load clusters.json if it exists.

    Returns the parsed dict, or None if the file is missing or unreadable.
    A missing file is a soft failure — the recommender still works,
    it just won't return related projects.
    """
    if not os.path.exists(_CLUSTERS_PATH):
        return None
    try:
        with open(_CLUSTERS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return None


def _get_related(recommended_ids, all_projects, cluster_data):
    """
    Find projects in the same cluster(s) as the recommended projects,
    excluding the ones already recommended.

    Returns up to MAX_RELATED project dicts.
    """
    clusters = cluster_data.get("clusters", {})  # {str(pid): cid}
    members  = cluster_data.get("members",  {})  # {str(cid): [pid, ...]}

    # Collect which clusters the recommended projects belong to.
    relevant_cluster_ids = set()
    for pid in recommended_ids:
        cid = clusters.get(str(pid))
        if cid is not None:
            relevant_cluster_ids.add(str(cid))

    if not relevant_cluster_ids:
        return []

    # Gather candidate IDs from those clusters, excluding already recommended.
    candidate_ids = []
    for cid in relevant_cluster_ids:
        for pid in members.get(cid, []):
            if pid not in recommended_ids and pid not in candidate_ids:
                candidate_ids.append(pid)

    id_to_project = {p["id"]: p for p in all_projects}
    related = [id_to_project[pid] for pid in candidate_ids if pid in id_to_project]
    return related[:MAX_RELATED]


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def project_matches_tech(project, tech_stack):
    """
    Check if a project matches the selected tech_stack using strict boundary checks.
    """
    if not tech_stack or tech_stack.lower() == "all":
        return True
        
    tech_stack = tech_stack.lower().strip()
    
    if tech_stack == "jsp":
        pattern = re.compile(r'\b(jsp|servlet|servlets)\b', re.IGNORECASE)
    elif tech_stack == "java":
        pattern = re.compile(r'\bjava\b', re.IGNORECASE)
    elif tech_stack == "javascript":
        pattern = re.compile(r'\b(javascript|js)\b', re.IGNORECASE)
    else:
        pattern = re.compile(rf'\b{re.escape(tech_stack)}\b', re.IGNORECASE)
        
    for skill in project.get("skills", []):
        if pattern.search(skill):
            return True
            
    for tech in project.get("tech_stack", []):
        if pattern.search(tech):
            return True
            
    return False


def get_recommendations(skills_string, level, interest, time_availability, tech_stack="all"):
    user_skills = parse_skills(skills_string)
    all_projects = load_all_projects()
    
    if tech_stack and tech_stack.lower() != "all":
        all_projects = [p for p in all_projects if project_matches_tech(p, tech_stack)]
        
    scored_projects = []
    graph = _load_skill_graph()
    for project in all_projects:
        score_result = score_single_project(
            project,
            user_skills,
            level,
            interest,
            time_availability,
        )
        if isinstance(score_result, tuple):
            rule_score, match_details = score_result
        else:
            rule_score, match_details = score_result, {}

        similarity_score = ml_similarity_score(
            project,
            user_skills,
            level,
            interest,
            time_availability,
            all_projects,
        )
        final_score = rule_score + similarity_score

        # Check relevance: project must match at least one user skill,
        # have a positive boost from the skill graph, or have a significant
        # ML semantic match (similarity_score >= 0.15).
        project_skills = [SKILL_ALIASES.get(s.lower(), s.lower()) for s in project.get("skills", [])]
        matched_skills = sum(1 for skill in user_skills if skill in project_skills)
        boost = gap_boost(user_skills, project_skills, graph)
        is_relevant = (matched_skills > 0) or (boost > 0) or (similarity_score >= 0.15)

        if final_score > 0 and is_relevant:
            scored_projects.append({
                "project": project,
                "score": final_score,
                "match_details": match_details
            })
    # Sort projects in descending order so the
    # most relevant recommendations appear first.
    scored_projects.sort(key=lambda item: (item["score"], item["project"].get("id", 0)), reverse=True)
    
    top_projects = []
    for item in scored_projects[:MAX_RESULTS]:
        proj = item["project"].copy()
        
        # Calculate theoretical max score for THIS project
        project_skills_count = len(proj.get("skills", []))
        theoretical_max = (project_skills_count * SCORING_WEIGHTS["skill"]) + \
                          SCORING_WEIGHTS["level"] + \
                          SCORING_WEIGHTS["interest"] + \
                          SCORING_WEIGHTS["time"] + 1.0  # +1.0 for max ML similarity
                          
        if theoretical_max == 0:
            theoretical_max = 1.0
            
        project_percentage = item["score"] / theoretical_max
        match_score = round(4.0 + (project_percentage * 6.0), 1)
        
        # Ensure it stays exactly within 4.0 to 10.0
        proj["match_score"] = min(max(match_score, 4.0), 10.0)
        
        match_details = item.get("match_details", {})
        
        # Construct distinct explanation
        import random
        
        matched_skills_list = match_details.get("matched_skills", [])
        skills_str = ""
        if matched_skills_list:
            skills_str = ", ".join(matched_skills_list[:3])
            if len(matched_skills_list) > 3:
                skills_str += f", and {len(matched_skills_list) - 3} more"
        
        # Determine components
        has_skills = bool(skills_str)
        has_level = bool(match_details.get("level"))
        has_interest = bool(match_details.get("interest"))
        
        # Build dynamic parts
        parts = []
        if has_skills:
            parts.append(f"utilizes your skills in {skills_str}")
        if has_level:
            parts.append("fits your current experience level")
        if has_interest:
            parts.append("aligns closely with your interests")
            
        project_title = proj.get("title", "this project")
            
        if not parts:
            explanation = f"We highly recommend '{project_title}' based on your overall profile."
        else:
            # Join the parts naturally
            if len(parts) == 1:
                reasons = parts[0]
            elif len(parts) == 2:
                reasons = f"{parts[0]} and {parts[1]}"
            else:
                reasons = f"{parts[0]}, {parts[1]}, and {parts[2]}"
                
            templates = [
                f"'{project_title}' is a great match because it {reasons}.",
                f"We recommend '{project_title}' as it {reasons}.",
                f"Based on your profile, '{project_title}' stands out because it {reasons}.",
                f"Dive into '{project_title}'! It's an excellent choice that {reasons}.",
                f"This project, '{project_title}', is ideal for you since it {reasons}."
            ]
            explanation = random.choice(templates)
            
        proj["match_explanation"] = explanation
        top_projects.append(proj)
        
    top_ids = [p["id"] for p in top_projects]
    
    cluster_data = _load_clusters()
    related = _get_related(top_ids, all_projects, cluster_data) if cluster_data else []
    
    graph = _load_skill_graph()
    progression = get_progression(user_skills, top_ids, all_projects, graph) if graph else []
    
    return {
        "recommendations": top_projects,
        "related": related,
        "progression": progression,
    }



def validate_recommendation_inputs(skills, level, interest, time_availability):
    errors = []

    if not skills or not skills.strip():
        errors.append("Please enter at least one skill.")
    elif not parse_skills(skills):
        errors.append("Please enter at least one valid skill.")

    if not level or not level.strip():
        errors.append("Please select an experience level.")
    elif level.strip().lower() not in VALID_LEVELS:
        errors.append("Invalid experience level. Choose Beginner, Intermediate, or Advanced.")

    if (
        not interest
        or not isinstance(interest, str)
        or interest.strip().lower() not in VALID_INTERESTS
    ):
        errors.append("Please select a valid area of interest.")

    if not time_availability or not time_availability.strip():
        errors.append("Please select your time availability.")
    elif time_availability.strip().lower() not in VALID_TIME_AVAILABILITY:
        errors.append("Invalid time availability. Choose Low, Medium, or High.")

    return errors