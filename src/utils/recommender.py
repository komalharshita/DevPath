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

VALID_LEVELS = {"beginner", "intermediate", "advanced"}
VALID_INTERESTS = {"web", "data", "education", "automation", "games", "cybersecurity", "devops", "backend", "tools", "productivity", "business logic", "mobile", "machine learning/ai"}
VALID_TIME_AVAILABILITY = {"low", "medium", "high"}
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

VALID_INTERESTS = {
    "web", "data", "education", "automation", "games",
    "cybersecurity", "devops", "mobile", "machine learning/ai",
    "artificial intelligence", "cloud computing", "mobile app development",
    "backend", "tools", "productivity", "business logic"
}
VALID_TIMES = {"low", "medium", "high"}

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

    if project.get("level", "").lower() == level.lower():
        score += SCORING_WEIGHTS["level"]

    p_interest = project.get("interest", "").lower()
    u_interest = interest.lower()
    # Use partial matching for interest as well
    if p_interest == u_interest or (u_interest and u_interest in p_interest) or (p_interest and p_interest in u_interest):
        score += SCORING_WEIGHTS["interest"]

    if project.get("time", "").lower() == time_availability.lower():
        score += SCORING_WEIGHTS["time"]
        
    graph = _load_skill_graph()
    score += gap_boost(user_skills, project_skills, graph)

    return score

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

def get_diagnostics(user_skills, level, interest, time_availability, all_projects):
    """
    Generate a helpful diagnostic message when no projects are recommended,
    explaining the most likely cause and suggesting valid alternatives.
    """
    # 1. Check for completely unmatched user skills
    all_project_skills = set()
    for p in all_projects:
        for s in p.get("skills", []):
            all_project_skills.add(SKILL_ALIASES.get(s.lower(), s.lower()))
            
    unmatched_skills = [s for s in user_skills if s not in all_project_skills]
    if unmatched_skills:
        skill_counts = Counter()
        for p in all_projects:
            for s in p.get("skills", []):
                skill_counts[SKILL_ALIASES.get(s.lower(), s.lower())] += 1
        popular_skills = [s.title() for s, _ in skill_counts.most_common(3)]
        
        def format_skill(s):
            if s.upper() in ["HTML", "CSS", "JS", "SQL", "AWS", "ETL", "API", "REST", "JSON"]:
                return s.upper()
            if s.lower() == "cpp":
                return "C++"
            return s.title()
            
        unmatched_str = ", ".join(f"'{format_skill(s)}'" for s in unmatched_skills)
        if len(popular_skills) > 1:
            popular_str = ", ".join(popular_skills[:-1]) + ", or " + popular_skills[-1]
        else:
            popular_str = popular_skills[0] if popular_skills else "other skills"
        return f"No projects match {unmatched_str}. Try {popular_str}."

    # 2. Check if the interest area has no projects at all
    all_interests = set(p.get("interest", "").lower() for p in all_projects if p.get("interest"))
    if interest.lower() not in all_interests:
        popular_interests = sorted(list(set(p.get("interest", "").title() for p in all_projects if p.get("interest"))))[:3]
        if len(popular_interests) > 1:
            popular_int_str = ", ".join(popular_interests[:-1]) + ", or " + popular_interests[-1]
        else:
            popular_int_str = popular_interests[0] if popular_interests else "other categories"
        return f"No projects match the interest '{interest.title()}'. Try {popular_int_str}."

    # 3. Check if time constraint is the blocker
    matching_level_and_interest = []
    for p in all_projects:
        p_level = p.get("level", "").lower()
        p_interest = p.get("interest", "").lower()
        u_level = level.lower()
        u_interest = interest.lower()
        
        level_match = (p_level == u_level)
        interest_match = (p_interest == u_interest or u_interest in p_interest or p_interest in u_interest)
        if level_match and interest_match:
            matching_level_and_interest.append(p)
            
    if matching_level_and_interest:
        TIME_RANKS = ["low", "medium", "high"]
        user_time = time_availability.strip().lower()
        time_blockers = []
        for p in matching_level_and_interest:
            p_time = p.get("time", "").strip().lower()
            if p_time in TIME_RANKS and user_time in TIME_RANKS:
                if TIME_RANKS.index(p_time) > TIME_RANKS.index(user_time):
                    time_blockers.append(p.get("time", "").title())
        if time_blockers:
            suggested_times = sorted(list(set(time_blockers)), key=lambda x: TIME_RANKS.index(x.lower()))
            if len(suggested_times) > 1:
                suggested_times_str = ", ".join(suggested_times[:-1]) + ", or " + suggested_times[-1]
            else:
                suggested_times_str = suggested_times[0]
            return f"No projects match '{time_availability.title()}' time availability. Try choosing {suggested_times_str} time."

    # 4. Check if experience level is the blocker for this interest
    matching_interest_only = []
    for p in all_projects:
        p_interest = p.get("interest", "").lower()
        u_interest = interest.lower()
        if p_interest == u_interest or u_interest in p_interest or p_interest in u_interest:
            matching_interest_only.append(p)
    if matching_interest_only:
        levels_available = sorted(list(set(p.get("level", "").title() for p in matching_interest_only)))
        if len(levels_available) > 1:
            levels_str = ", ".join(levels_available[:-1]) + ", or " + levels_available[-1]
        else:
            levels_str = levels_available[0]
        return f"No projects match '{level.title()}' level for interest '{interest.title()}'. Try choosing {levels_str}."

    return "No projects matched your inputs. Try different skills or broaden your interest area."


def get_recommendations(skills_string, level, interest, time_availability):
    user_skills = parse_skills(skills_string)
    all_projects = load_all_projects()
    scored_projects = []
    for project in all_projects:
        rule_score = score_single_project(
            project,
            user_skills,
            level,
            interest,
            time_availability,
        )
        similarity_score = ml_similarity_score(
            project,
            user_skills,
            level,
            interest,
            time_availability,
            all_projects,
        )
        final_score = rule_score + similarity_score
        if final_score > 0:
            scored_projects.append({
                "project": project,
                "score": final_score,
            })
    # Sort projects in descending order so the
    # most relevant recommendations appear first.
    scored_projects.sort(key=lambda item: (item["score"], item["project"].get("id", 0)), reverse=True)
    
    top_projects = [item["project"] for item in scored_projects[:MAX_RESULTS]]
    top_ids = [p["id"] for p in top_projects]
    
    cluster_data = _load_clusters()
    related = _get_related(top_ids, all_projects, cluster_data) if cluster_data else []
    
    graph = _load_skill_graph()
    progression = get_progression(user_skills, top_ids, all_projects, graph) if graph else []
    
    message = None
    if not top_projects:
        message = get_diagnostics(user_skills, level, interest, time_availability, all_projects)
        
    return {
        "recommendations": top_projects,
        "related": related,
        "progression": progression,
        "message": message,
    }

# NOTE: VALID_LEVELS, VALID_INTERESTS, and VALID_TIME_AVAILABILITY are
# defined at the top of this module. Do not redefine them here.


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

    if not interest or not isinstance(interest, str) or not interest.strip():
        errors.append("Please select an area of interest.")

    if not time_availability or not time_availability.strip():
        errors.append("Please select your time availability.")
    elif time_availability.strip().lower() not in VALID_TIME_AVAILABILITY:
        errors.append("Invalid time availability. Choose Low, Medium, or High.")

    return errors