# utils/recommender.py
# Contains all recommendation logic: scoring and filtering projects.

import math
import re
from collections import Counter
import functools

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

_cached_clusters = None
_clusters_loaded = False
_cached_skill_graph = None
_skill_graph_loaded = False

def clear_caches():
    """Clear all in-memory JSON caches."""
    global _cached_clusters, _clusters_loaded, _cached_skill_graph, _skill_graph_loaded
    _cached_clusters = None
    _clusters_loaded = False
    _cached_skill_graph = None
    _skill_graph_loaded = False

VALID_LEVELS = {"beginner", "intermediate", "advanced"}
VALID_INTERESTS = {"web", "data", "education", "automation", "games", "cybersecurity", "devops", "backend", "tools", "productivity", "business logic", "mobile", "machine learning/ai"}
VALID_TIME_AVAILABILITY = {"low", "medium", "high"}
SCORING_WEIGHTS = {
    "skill": 3,
    "level": 2,
    "interest": 2,
    "time": 1,
}



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
def _normalize_skill(s: str) -> str:
    """Normalize a skill string: strip surrounding whitespace and lowercase."""
    return s.strip().lower()


def parse_skill_entries(skills_string):
    """Parse skills with optional per-skill proficiency levels."""
    stripped = skills_string.strip()

    if stripped.startswith("["):
        try:
            parsed = json.loads(stripped)
            if isinstance(parsed, list):
                entries = []
                for item in parsed:
                    if isinstance(item, dict):
                        skill = _normalize_skill(str(item.get("skill", "")))
                        proficiency = str(item.get("proficiency", "Beginner")).strip().title()
                    else:
                        skill = _normalize_skill(str(item))
                        proficiency = "Beginner"

                    if skill:
                        entries.append(
                            {
                                "skill": SKILL_ALIASES.get(skill, skill),
                                "proficiency": (
                                    proficiency
                                    if proficiency in (
                                        "Beginner",
                                        "Intermediate",
                                        "Advanced",
                                    )
                                    else "Beginner"
                                ),
                            }
                        )
                return entries
        except (json.JSONDecodeError, ValueError):
            pass

    return [
        {
            "skill": SKILL_ALIASES.get(_normalize_skill(skill), _normalize_skill(skill)),
            "proficiency": "Beginner",
        }
        for skill in skills_string.split(",")
        if skill.strip()
    ]


def parse_skills(skills_string):
    return [entry["skill"] for entry in parse_skill_entries(skills_string)]


def parse_skills(skills_string):
    return [entry["skill"] for entry in parse_skill_entries(skills_string)]

_nlp_model = None
_project_embeddings_cache = {}

def get_nlp_model():
    """Lazily load the SentenceTransformer model to save startup time."""
    global _nlp_model
    if _nlp_model is None:
        try:
            from sentence_transformers import SentenceTransformer
            _nlp_model = SentenceTransformer('all-MiniLM-L6-v2')
        except Exception as e:
            print(f"Error loading NLP model: {e}")
            pass
    return _nlp_model

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
    return f"I am a {level} developer interested in {interest}. I have {time_availability} time. My skills are: {', '.join(user_skills)}."

@functools.lru_cache(maxsize=128)
def _get_user_embedding(user_text):
    model = get_nlp_model()
    if not model:
        return None
    return model.encode(user_text, convert_to_tensor=True)

def _get_project_embedding(project):
    model = get_nlp_model()
    if not model:
        return None
        
    pid = project.get("id")
    if pid not in _project_embeddings_cache:
        text = _project_text(project)
        _project_embeddings_cache[pid] = model.encode(text, convert_to_tensor=True)
        
    return _project_embeddings_cache[pid]

def ml_similarity_score(project, user_skills, level, interest, time_availability):
    """
    Computes semantic similarity between the user's profile and the project using NLP embeddings.
    """
    model = get_nlp_model()
    if not model:
        return 0.0
        
    user_str = _user_text(user_skills, level, interest, time_availability)
    user_emb = _get_user_embedding(user_str)
    proj_emb = _get_project_embedding(project)
    
    if user_emb is None or proj_emb is None:
        return 0.0
        
    from sentence_transformers import util
    cos_sim = util.cos_sim(user_emb, proj_emb)
    
    # cos_sim is a 2D tensor, get the scalar value
    return cos_sim.item()

def _tokenize(text):
    return re.findall(r"[a-z0-9]+", str(text).lower())

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

def tfidf_similarity_score(project, user_vector, idf_scores):
    project_vector = _tfidf_vector(_tokenize(_project_text(project)), idf_scores)
    return _cosine_similarity(user_vector, project_vector)

def score_single_project(project, user_skills, level, interest, time_availability, graph=None, skill_proficiencies=None):
    TIME_RANKS = ["low", "medium", "high"]

    user_time    = time_availability.strip().lower()
    project_time = project.get("time", "").strip().lower()

    # If the project needs more time than the user has, exclude it.
    if project_time not in TIME_RANKS or user_time not in TIME_RANKS:
        return 0, {}
    if TIME_RANKS.index(project_time) > TIME_RANKS.index(user_time):
        return 0, {}

    score = 0

    # Compare user's skills against the project's required skills
    project_skills = [SKILL_ALIASES.get(_normalize_skill(s), _normalize_skill(s)) for s in project.get("skills", [])]
    matched_skills = sum(1 for skill in user_skills if skill in project_skills)
    proficiency_weights = {
        "beginner": 1.0,
        "intermediate": 1.5,
        "advanced": 2.0,
    }
    skill_proficiencies = skill_proficiencies or {}
    weighted_skill_score = sum(
        proficiency_weights.get(skill_proficiencies.get(skill, "Beginner").lower(), 1.0)
        for skill in user_skills
        if skill in project_skills
    )
    if project_skills:
        coverage = matched_skills / len(project_skills)
        score += weighted_skill_score * SCORING_WEIGHTS["skill"] * coverage
    else:
        score += weighted_skill_score * SCORING_WEIGHTS["skill"]

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
        
    if graph is None:
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
    global _cached_skill_graph, _skill_graph_loaded
    if _skill_graph_loaded:
        return _cached_skill_graph
        
    _skill_graph_loaded = True
    path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "data", "skill_graph.json"
    )
    if not os.path.exists(path):
        _cached_skill_graph = {}
        return _cached_skill_graph
    try:
        with open(path, "r", encoding="utf-8") as f:
            _cached_skill_graph = json.load(f)
    except (json.JSONDecodeError, OSError):
        _cached_skill_graph = {}
    return _cached_skill_graph


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
            SKILL_ALIASES.get(_normalize_skill(s), _normalize_skill(s))
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
    global _cached_clusters, _clusters_loaded
    if _clusters_loaded:
        return _cached_clusters
        
    _clusters_loaded = True
    if not os.path.exists(_CLUSTERS_PATH):
        _cached_clusters = None
        return _cached_clusters
    try:
        with open(_CLUSTERS_PATH, "r", encoding="utf-8") as f:
            _cached_clusters = json.load(f)
    except (json.JSONDecodeError, OSError):
        _cached_clusters = None
    return _cached_clusters


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
        pattern = re.compile(r"\b(jsp|servlet|servlets)\b", re.IGNORECASE)
    elif tech_stack == "java":
        pattern = re.compile(r"\bjava\b", re.IGNORECASE)
    elif tech_stack == "javascript":
        pattern = re.compile(r"\b(javascript|js)\b", re.IGNORECASE)
    else:
        pattern = re.compile(rf"\b{re.escape(tech_stack)}\b", re.IGNORECASE)

    for skill in project.get("skills", []):
        if pattern.search(skill):
            return True

    for tech in project.get("tech_stack", []):
        if pattern.search(tech):
            return True

    return False


def get_recommendations(
    skills_string,
    level,
    interest,
    time_availability,
    tech_stack="all",
    max_results=None,
):
    skill_entries = parse_skill_entries(skills_string)

    user_skills = [entry["skill"] for entry in skill_entries]

    skill_proficiencies = {
        entry["skill"]: entry["proficiency"]
        for entry in skill_entries
    }
    all_projects = load_all_projects()
    
    # Load NLP model to determine if we should use semantic search
    model = get_nlp_model()
    
    # Pre-compute TF-IDF vectors ONLY if fallback is needed
    if not model:
        project_documents = [_tokenize(_project_text(p)) for p in all_projects]
        user_tokens = _tokenize(_user_text(user_skills, level, interest, time_availability))
        idf_scores = _idf(project_documents + [user_tokens])
        user_vector = _tfidf_vector(user_tokens, idf_scores)
    
    scored_projects = []
    graph = _load_skill_graph()
    for project in all_projects:
        score_result = score_single_project(
            project,
            user_skills,
            level,
            interest,
            time_availability,
            graph,
        )
        if isinstance(score_result, tuple):
            rule_score, match_details = score_result
        else:
            rule_score, match_details = score_result, {}

        if model:
            similarity_score = ml_similarity_score(
                project,
                user_skills,
                level,
                interest,
                time_availability,
            )
        else:
            similarity_score = tfidf_similarity_score(
                project,
                user_vector,
                idf_scores
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
    
    selected_projects = (
      scored_projects
      if max_results is None
      else scored_projects[:max_results])

    top_projects = []

    for item in selected_projects:
      proj = item["project"].copy()

      # Calculate theoretical max score for THIS project
      project_skills_count = len(proj.get("skills", []))
      theoretical_max = (
        project_skills_count * SCORING_WEIGHTS["skill"]
        + SCORING_WEIGHTS["level"]
        + SCORING_WEIGHTS["interest"]
        + SCORING_WEIGHTS["time"]
        + 1.0
      )

      if theoretical_max == 0:
        theoretical_max = 1.0

      project_percentage = item["score"] / theoretical_max
      match_score = round(4.0 + (project_percentage * 6.0), 1)

      # Ensure it stays exactly within 4.0 to 10.0
      proj["match_score"] = min(max(match_score, 4.0), 10.0)

      match_details = item.get("match_details", {})

      import random

      matched_skills_list = match_details.get("matched_skills", [])
      skills_str = ""

      if matched_skills_list:
        skills_str = ", ".join(matched_skills_list[:3])
        if len(matched_skills_list) > 3:
          skills_str += f", and {len(matched_skills_list) - 3} more"

      has_skills = bool(skills_str)
      has_level = bool(match_details.get("level"))
      has_interest = bool(match_details.get("interest"))

      parts = []
      if has_skills:
        parts.append(f"utilizes your skills in {skills_str}")
      if has_level:
        parts.append("fits your current experience level")
      if has_interest:
        parts.append("aligns closely with your interests")

      project_title = proj.get("title", "this project")
      if not parts:
          explanation = (
              f"We highly recommend '{project_title}' based on your overall profile."
          )
      else:
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
              f"This project, '{project_title}', is ideal for you since it {reasons}.",
          ]

          explanation = random.choice(templates)

      proj["match_explanation"] = explanation
      top_projects.append(proj)      
    top_ids = [p["id"] for p in top_projects]

    cluster_data = _load_clusters()
    related = _get_related(top_ids, all_projects, cluster_data) if cluster_data else []
    
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