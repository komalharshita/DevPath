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
    
    return {
        "recommendations": top_projects,
        "related": related,
        "progression": progression,
    }

VALID_LEVELS = ["beginner", "intermediate", "advanced"]
VALID_TIME_AVAILABILITY = ["low", "medium", "high"]


VALID_LEVELS = ["beginner", "intermediate", "advanced"]
VALID_INTERESTS = ["data", "web", "backend", "cybersecurity", "games", "education", "automation"]
VALID_TIME_AVAILABILITY = ["low", "medium", "high"]


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