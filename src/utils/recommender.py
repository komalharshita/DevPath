"""
# utils/recommender.py
# Contains all recommendation logic: scoring and filtering projects.
"""

import math
import re
from collections import Counter
from pathlib import Path
import json
import os

from utils.data_loader import load_all_projects

# =============================================================================
# Configuration loader
# =============================================================================

_CONFIG_PATH = Path(__file__).parent.parent / "data" / "scoring_config.json"

def load_scoring_config() -> dict:
    """
    Load scoring weights and thresholds from data/scoring_config.json.
    
    Returns:
        dict: Configuration dictionary with weights and thresholds.
    
    Raises:
        FileNotFoundError: If config file doesn't exist.
    """
    if not _CONFIG_PATH.exists():
        raise FileNotFoundError(
            f"Scoring config not found at {_CONFIG_PATH}. "
            "Copy data/scoring_config.json.example if it's missing, "
            "or restore data/scoring_config.json."
        )
    with open(_CONFIG_PATH, encoding='utf-8-sig') as f:  # Changed from 'utf-8' to 'utf-8-sig'
        return json.load(f)

# Load config once at module level
try:
    _CONFIG = load_scoring_config()
    SCORING_WEIGHTS = _CONFIG.get("weights", {})
    MIN_SCORE_THRESHOLD = _CONFIG.get("minimum_score_threshold", 1)
    MAX_RESULTS = _CONFIG.get("result_count", 3)
    MAX_HOPS = _CONFIG.get("max_hops", 3)
    ML_SIMILARITY_WEIGHT = _CONFIG.get("ml_similarity_weight", 0.5)
except FileNotFoundError:
    # Fallback defaults if config file is missing (shouldn't happen in production)
    SCORING_WEIGHTS = {
        "skill_match_per_skill": 3,
        "level_exact_match": 2,
        "interest_match": 2,
        "time_match": 1,
        "gap_boost_base": 1.0
    }
    MIN_SCORE_THRESHOLD = 1
    MAX_RESULTS = 3
    MAX_HOPS = 3
    ML_SIMILARITY_WEIGHT = 0.5
    print(f"Warning: Scoring config not found at {_CONFIG_PATH}. Using defaults.")

MAX_RELATED = 3
_CLUSTERS_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "data",
    "clusters.json",
)

VALID_LEVELS = {"beginner", "intermediate", "advanced"}
VALID_INTERESTS = {
    "web", "data", "education", "automation", "games", 
    "cybersecurity", "devops", "backend", "tools", "productivity", 
    "business logic", "mobile", "machine learning/ai",
    "artificial intelligence", "cloud computing", "mobile app development"
}
VALID_TIME_AVAILABILITY = {"low", "medium", "high"}

# Common aliases and abbreviations for skills
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


def score_project(project: dict, user_input: dict, weights: dict) -> int:
    """
    Score a single project based on user input and configuration weights.
    
    Args:
        project: Project dictionary with skills, level, interest, time
        user_input: User input dict with skills, level, interest, time
        weights: Scoring weights from config
    
    Returns:
        int: Score for the project
    """
    score = 0
    
    # Skills match
    user_skills = set(s.lower() for s in user_input.get("skills", []))
    project_skills = set(s.lower() for s in project.get("skills", []))
    
    # Number of matching skills × weight per skill
    score += len(user_skills & project_skills) * weights.get("skill_match_per_skill", 3)
    
    # Level match
    if project.get("level", "").lower() == user_input.get("level", "").lower():
        score += weights.get("level_exact_match", 2)
    
    # Interest match
    if project.get("interest", "").lower() == user_input.get("interest", "").lower():
        score += weights.get("interest_match", 2)
    
    # Time match
    if project.get("time", "").lower() == user_input.get("time", "").lower():
        score += weights.get("time_match", 1)
    
    return score


def _score_with_time_filter(project, user_input, weights):
    """
    Apply time availability filtering then score the project.
    If time doesn't match, return 0.
    """
    TIME_RANKS = ["low", "medium", "high"]
    
    user_time = user_input.get("time", "").strip().lower()
    project_time = project.get("time", "").strip().lower()
    
    # Time availability filtering
    if project_time not in TIME_RANKS or user_time not in TIME_RANKS:
        return 0
    if TIME_RANKS.index(project_time) > TIME_RANKS.index(user_time):
        return 0
    
    # Base score
    score = score_project(project, user_input, weights)
    
    # Add graph-based boost if available
    graph = _load_skill_graph()
    user_skills = [s.lower() for s in user_input.get("skills", [])]
    project_skills = [s.lower() for s in project.get("skills", [])]
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


def _hops_to_skill(target, user_skills, graph, max_hops=MAX_HOPS):
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
    gap_boost_base = SCORING_WEIGHTS.get("gap_boost_base", 1.0)
    
    for skill in project_skills:
        if skill not in user_skills:
            hops = _hops_to_skill(skill, user_skills, graph)
            if hops and hops > 0:
                boost += gap_boost_base / hops
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
    clusters = cluster_data.get("clusters", {})
    members = cluster_data.get("members", {})

    relevant_cluster_ids = set()
    for pid in recommended_ids:
        cid = clusters.get(str(pid))
        if cid is not None:
            relevant_cluster_ids.add(str(cid))

    if not relevant_cluster_ids:
        return []

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
    """
    Get project recommendations based on user input.
    
    Args:
        skills_string: Comma-separated or JSON array of skills
        level: User experience level
        interest: User's area of interest
        time_availability: User's available time
    
    Returns:
        dict: Contains recommendations, related projects, and progression
    """
    # Parse user input
    user_skills = parse_skills(skills_string)
    user_input = {
        "skills": user_skills,
        "level": level,
        "interest": interest,
        "time": time_availability
    }
    
    # Load configuration
    weights = SCORING_WEIGHTS
    
    all_projects = load_all_projects()
    scored_projects = []
    
    for project in all_projects:
        # Rule-based scoring with time filter
        rule_score = _score_with_time_filter(project, user_input, weights)
        
        # ML similarity score
        similarity_score = ml_similarity_score(
            project,
            user_skills,
            level,
            interest,
            time_availability,
            all_projects,
        )
        
        # Combine scores with ML weight from config
        final_score = rule_score + (ML_SIMILARITY_WEIGHT * similarity_score)
        
        if final_score >= MIN_SCORE_THRESHOLD:
            scored_projects.append({
                "project": project,
                "score": final_score,
            })
    
    # Sort projects by score descending
    scored_projects.sort(key=lambda item: (item["score"], item["project"].get("id", 0)), reverse=True)
    
    # Get top recommendations
    top_projects = [item["project"] for item in scored_projects[:MAX_RESULTS]]
    top_ids = [p["id"] for p in top_projects]
    
    # Get related projects from clusters
    cluster_data = _load_clusters()
    related = _get_related(top_ids, all_projects, cluster_data) if cluster_data else []
    
    # Get progression projects
    graph = _load_skill_graph()
    progression = get_progression(user_skills, top_ids, all_projects, graph) if graph else []
    
    return {
        "recommendations": top_projects,
        "related": related,
        "progression": progression,
    }


# Validation functions
VALID_LEVELS_LIST = ["beginner", "intermediate", "advanced"]
VALID_INTERESTS_LIST = ["data", "web", "backend", "cybersecurity", "games", "education", "automation"]
VALID_TIME_AVAILABILITY_LIST = ["low", "medium", "high"]


def validate_recommendation_inputs(skills, level, interest, time_availability):
    """
    Validate user inputs for recommendation.
    
    Returns:
        list: List of error messages, empty if all valid.
    """
    errors = []

    if not skills or not skills.strip():
        errors.append("Please enter at least one skill.")
    elif not parse_skills(skills):
        errors.append("Please enter at least one valid skill.")

    if not level or not level.strip():
        errors.append("Please select an experience level.")
    elif level.strip().lower() not in VALID_LEVELS_LIST:
        errors.append("Invalid experience level. Choose Beginner, Intermediate, or Advanced.")

    if not interest or not isinstance(interest, str) or not interest.strip():
        errors.append("Please select an area of interest.")

    if not time_availability or not time_availability.strip():
        errors.append("Please select your time availability.")
    elif time_availability.strip().lower() not in VALID_TIME_AVAILABILITY_LIST:
        errors.append("Invalid time availability. Choose Low, Medium, or High.")

    return errors


def recommend(user_input: dict) -> list:
    """
    Alternative API for recommendations using dict input.
    This maintains backward compatibility with existing imports.
    
    Args:
        user_input: Dict with keys: skills, level, interest, time
    
    Returns:
        list: List of recommended project dictionaries
    """
    config = load_scoring_config()
    weights = config["weights"]
    
    # Parse skills if provided as string
    skills = user_input.get("skills", "")
    if isinstance(skills, str):
        parsed_skills = parse_skills(skills)
    else:
        parsed_skills = skills
    
    # Convert to format expected by get_recommendations
    result = get_recommendations(
        skills_string=", ".join(parsed_skills) if isinstance(skills, str) else skills,
        level=user_input.get("level", ""),
        interest=user_input.get("interest", ""),
        time_availability=user_input.get("time", "")
    )
    
    return result["recommendations"]