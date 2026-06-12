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

SKILL_ALIASES = {
    "js": "javascript",
    "py": "python",
    "html5": "html",
    "css3": "css",
    "c++": "cpp",
    "web dev": "javascript",
}

def parse_skills(skills_string):
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
    score = 0

    # Compare user's skills against the project's required skills
    project_skills = [SKILL_ALIASES.get(s.lower(), s.lower()) for s in project.get("skills", [])]
    # Count how many user skills overlap with the
    # skills required by the current project.
    matched_skills = sum(1 for skill in user_skills if skill in project_skills)

    score += matched_skills * SCORING_WEIGHTS["skill"]

    if project.get("level", "").lower() == level.lower():
        score += SCORING_WEIGHTS["level"]

    if project.get("interest", "").lower() == interest.lower():
        score += SCORING_WEIGHTS["interest"]

    if project_time == user_time:
        score += SCORING_WEIGHTS["time"]

    return score

# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def get_recommendations(skills_string, level, interest, time_availability):
    user_skills = parse_skills(skills_string)
    all_projects = load_all_projects()

    scored = []
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

    scored_projects.sort(key=lambda item: item["score"], reverse=True)

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