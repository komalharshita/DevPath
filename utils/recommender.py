# utils/recommender.py
# Contains all recommendation logic: scoring and filtering projects.

import math
import re
from collections import Counter
import json
import os
from utils.data_loader import load_all_projects

MAX_RESULTS = 3

SCORING_WEIGHTS = {
    "skill": 3,
    "level": 2,
    "interest": 2,
    "time": 1,
}

# Add backward compatibility for the existing test suite
WEIGHT_SKILL = SCORING_WEIGHTS["skill"]
WEIGHT_LEVEL = SCORING_WEIGHTS["level"]
WEIGHT_INTEREST = SCORING_WEIGHTS["interest"]
WEIGHT_TIME = SCORING_WEIGHTS["time"]

VALID_LEVELS = ["beginner", "intermediate", "advanced"]
VALID_INTERESTS = [
    "web", "data", "education", "automation", "games", 
    "cybersecurity", "devops", "backend", "tools", 
    "productivity", "business logic", "mobile", "machine learning/ai"
]
VALID_TIME_AVAILABILITY = ["low", "medium", "high"]

SKILL_ALIASES = {
    "js": "javascript",
    "py": "python",
    "html5": "html",
    "css3": "css",
    "c++": "cpp",
    "web dev": "javascript",
}

def parse_skills(skills_string):
    if not skills_string:
        return []
        
    try:
        # Attempt to parse as JSON first (new frontend sends JSON array)
        parsed = json.loads(skills_string)
        if isinstance(parsed, list):
            raw_skills = [str(s).strip().lower() for s in parsed if str(s).strip()]
        else:
            raw_skills = [str(parsed).strip().lower()]
    except (json.JSONDecodeError, TypeError):
        # Fallback to comma-separated string (legacy fallback)
        raw_skills = [s.strip().lower() for s in str(skills_string).split(",") if s.strip()]

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

    return dot_product / (magnitude_b * magnitude_b)

def ml_similarity_score(project, user_skills, level, interest, time_availability, all_projects):
    project_documents = [_tokenize(_project_text(p)) for p in all_projects]
    user_tokens = _tokenize(_user_text(user_skills, level, interest, time_availability))

    idf_scores = _idf(project_documents + [user_tokens])

    user_vector = _tfidf_vector(user_tokens, idf_scores)
    project_vector = _tfidf_vector(_tokenize(_project_text(project)), idf_scores)

    return _cosine_similarity(user_vector, project_vector)

def score_single_project(project, user_skills, level, interest, time_availability):
    score = 0

    # Normalize project skills so aliases (e.g. js -> javascript) are handled
    project_skills = [
        SKILL_ALIASES.get(skill.lower(), skill.lower())
        for skill in project.get("skills", [])
    ]

    # Skill score:
    # score = matched_skills * weight * coverage
    # coverage = matched_skills / total_project_skills
    if project_skills:
        matched_skills = len(set(user_skills) & set(project_skills))
        coverage = matched_skills / len(project_skills)
        score += (
            matched_skills
            * SCORING_WEIGHTS["skill"]
            * coverage
        )

    # Experience level match
    if project.get("level", "").lower() == level.lower():
        score += SCORING_WEIGHTS["level"]

    # Interest match
    if project.get("interest", "").lower() == interest.lower():
        score += SCORING_WEIGHTS["interest"]

    # Time availability match
    if project.get("time", "").lower() == time_availability.lower():
        score += SCORING_WEIGHTS["time"]

    return score

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
            all_projects,
        )

        final_score = rule_score + similarity_score

        if final_score > 0:
            scored_projects.append({
                "project": project,
                "score": final_score,
            })
            
    # Sort projects in descending order so the most relevant recommendations appear first.
    scored_projects.sort(key=lambda item: (item["score"], item["project"].get("id", 0)), reverse=True)

    return [item["project"] for item in scored_projects[:MAX_RESULTS]]

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

    if not interest or not isinstance(interest, str) or interest.strip().lower() not in VALID_INTERESTS:
        errors.append("Please select a valid area of interest.")

    if not time_availability or not time_availability.strip():
        errors.append("Please select your time availability.")
    elif time_availability.strip().lower() not in VALID_TIME_AVAILABILITY:
        errors.append("Invalid time availability. Choose Low, Medium, or High.")

    return errors