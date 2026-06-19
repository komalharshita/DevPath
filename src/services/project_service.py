# services/project_service.py
import json
import math
import os
import re
import threading
import logging
from collections import Counter

from repositories.project_repository import (
    load_raw_projects,
    find_project_by_id as repo_find_project_by_id,
    clear_cache as repo_clear_cache
)
from services.url_validator_service import is_valid_url, parse_resource

logger = logging.getLogger("devpath.project_service")

# Thread lock and cache for validated projects
_validated_projects_cache = None
_service_lock = threading.Lock()

# Recommender Constants
MAX_RESULTS = 3
MAX_RELATED = 3
_CLUSTERS_PATH = os.path.normpath(
    os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data", "clusters.json")
)

SCORING_WEIGHTS = {
    "skill": 3,
    "level": 2,
    "interest": 2,
    "time": 1,
}

SKILL_ALIASES = {
    "js": "javascript",
    "py": "python",
    "html5": "html",
    "css3": "css",
    "c++": "cpp",
    "web dev": "javascript",
}

VALID_LEVELS = ["beginner", "intermediate", "advanced"]
VALID_TIME_AVAILABILITY = ["low", "medium", "high"]


def validate_projects(projects):
    """Validate project dataset integrity."""
    seen_ids = set()
    seen_titles = set()

    required_fields = [
        "id", "title", "skills", "level", "interest", "time",
        "description", "features", "tech_stack", "roadmap",
        "resources", "starter_code"
    ]

    for project in projects:
        # Required fields
        for field in required_fields:
            if field not in project:
                raise ValueError(f"Missing required field: {field}")

            if isinstance(project[field], str) and not project[field].strip():
                raise ValueError(
                    f"Empty value for field '{field}' in project '{project.get('title', 'Unknown')}'"
                )

        # Duplicate IDs
        project_id = project["id"]
        if project_id in seen_ids:
            raise ValueError(f"Duplicate project ID found: {project_id}")
        seen_ids.add(project_id)

        # Duplicate Titles
        title = " ".join(project["title"].split()).lower()
        if title in seen_titles:
            raise ValueError(f"Duplicate project title found: {project['title']}")
        seen_titles.add(title)

        # Resource URL format validation
        for raw in project.get("resources", []):
            parsed = parse_resource(raw)
            url = parsed.get("url", "")
            if url and not is_valid_url(url):
                logger.warning(
                    "Malformed resource URL in project '%s' (id=%s): %r",
                    project.get("title", "Unknown"),
                    project_id,
                    url,
                )


def load_all_projects():
    """Load, validate, and return the projects list (cached)."""
    global _validated_projects_cache
    if _validated_projects_cache is None:
        with _service_lock:
            if _validated_projects_cache is None:
                projects = load_raw_projects()
                validate_projects(projects)
                _validated_projects_cache = projects
    return _validated_projects_cache


def find_project_by_id(project_id):
    """Find and return the project matching project_id, or None."""
    # Rely on validated projects cache to guarantee data integrity
    projects = load_all_projects()
    for p in projects:
        if p.get("id") == project_id:
            return p
    return None


def clear_cache():
    """Clear both the service-level validated cache and the repository cache."""
    global _validated_projects_cache
    with _service_lock:
        _validated_projects_cache = None
    repo_clear_cache()


def get_available_levels():
    """Return all unique project levels."""
    projects = load_all_projects()
    return sorted({p["level"] for p in projects})


def get_project_stats():
    """Return total_projects, unique_skills, and beginner_friendly counts."""
    projects = load_all_projects()

    all_skills = set()
    beginner_friendly = 0
    for p in projects:
        for s in p.get("skills", []):
            all_skills.add(s)
        if p.get("level") == "Beginner":
            beginner_friendly += 1

    return {
        "total_projects": len(projects),
        "unique_skills": len(all_skills),
        "beginner_friendly": beginner_friendly,
    }


def parse_skills(skills_string):
    """Convert a raw skills string into a normalized lowercase list."""
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

    if project_time not in TIME_RANKS or user_time not in TIME_RANKS:
        return 0
    if TIME_RANKS.index(project_time) > TIME_RANKS.index(user_time):
        return 0

    score = 0

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
    if p_interest == u_interest or (u_interest and u_interest in p_interest) or (p_interest and p_interest in u_interest):
        score += SCORING_WEIGHTS["interest"]

    if project.get("time", "").lower() == time_availability.lower():
        score += SCORING_WEIGHTS["time"]
        
    graph = _load_skill_graph()
    score += gap_boost(user_skills, project_skills, graph)

    return score


def _load_skill_graph():
    path = os.path.normpath(
        os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            "data", "skill_graph.json"
        )
    )
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def _hops_to_skill(target, user_skills, graph, max_hops=3):
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
    boost = 0.0
    for skill in project_skills:
        if skill not in user_skills:
            hops = _hops_to_skill(skill, user_skills, graph)
            if hops and hops > 0:
                boost += 1.0 / hops
    return round(boost, 3)


def get_progression(user_skills, recommended_ids, all_projects, graph):
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
        if any(s in reachable for s in project_skills):
            boost = gap_boost(user_skills, project_skills, graph)
            progression.append({
                "project": project,
                "gap_score": boost
            })
            
    progression.sort(key=lambda x: x["gap_score"], reverse=True)
    return progression[:3]


def _load_clusters():
    if not os.path.exists(_CLUSTERS_PATH):
        return None
    try:
        with open(_CLUSTERS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return None


def _get_related(recommended_ids, all_projects, cluster_data):
    clusters = cluster_data.get("clusters", {})
    members  = cluster_data.get("members",  {})

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
