# utils/recommender.py
# Contains all recommendation logic: scoring and filtering projects.
# Kept separate from routing so it can be tested and extended independently.

from utils.data_loader import load_all_projects

# Maximum number of recommendations returned to the user
MAX_RESULTS = 3

# Scoring weights used by the recommendation engine.
# Higher weights mean that criterion has more influence
# on the final recommendation score.
WEIGHT_SKILL = 3   # highest because they best reflect project compatibility
WEIGHT_LEVEL = 2   # helps avoid projects that are too easy or too difficult
WEIGHT_INTEREST = 2   # Interest alignment improves recommendation relevance
WEIGHT_TIME = 1    # Time availability acts as a smaller tie-breaker factor


# Common aliases and abbreviations for skills
# This improves recommendation accuracy by normalizing user input
SKILL_ALIASES = {
    "js": "javascript",
    "py": "python",
    "html5": "html",
    "css3": "css",
    "c++": "cpp",
    "web dev": "javascript"
}


def parse_skills(skills_string):
    """
    Convert a raw comma-separated skills string into
    a normalized lowercase list.

    Example:
    "JS, HTML5, CSS3" -> ["javascript", "html", "css"]
    """

    raw_skills = [
        s.strip().lower()
        for s in skills_string.split(",")
        if s.strip()
    ]

    normalized_skills = [
        SKILL_ALIASES.get(skill, skill)
        for skill in raw_skills
    ]

    return normalized_skills


def score_single_project(
        project, user_skills,
        level, interest, time_availability):
    """
    Calculate a numeric relevance score for one project.

    Each matching criterion adds points:
      - Each matching skill:  +3
      - Level match:          +2
      - Interest match:       +2
      - Time match:           +1

    Returns an integer score (0 means no match at all).
    """
    score = 0

    # Compare user's skills against the project's required skills
    project_skills = [s.lower() for s in project.get("skills", [])]
    # Count how many user skills overlap with the
    # skills required by the current project.
    matched_skills = sum(1 for skill in user_skills if skill in project_skills)
    # Add weighted points based on the number of matching skills.
    # More overlapping skills result in a higher recommendation score.
    score += matched_skills * WEIGHT_SKILL

    # Award points for each additional matching criterion
    if project.get("level", "").lower() == level.lower():
        score += WEIGHT_LEVEL

    if project.get("interest", "").lower() == interest.lower():
        score += WEIGHT_INTEREST

    if project.get("time", "").lower() == time_availability.lower():
        score += WEIGHT_TIME

    return score


def explain_project_match(project, user_skills, level, interest, time_availability):
    """
  Build a breakdown of why a project matched the user's inputs.
  Used by the API so the UI can show transparent scoring.
    """
    matched_skills = [
        skill for skill in project.get("skills", [])
        if skill.lower() in user_skills
    ]

    level_match = project.get("level", "").lower() == level.lower()
    interest_match = project.get("interest", "").lower() == interest.lower()
    time_match = project.get("time", "").lower() == time_availability.lower()

    score = score_single_project(
        project, user_skills, level, interest, time_availability
    )

    missing_skills = [
        skill for skill in project.get("skills", [])
        if skill.lower() not in user_skills
    ]

    return {
        "score": score,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "level_match": level_match,
        "interest_match": interest_match,
        "time_match": time_match,
    }


def get_recommendations(skills_string, level, interest, time_availability):
    """
    Return the top N recommended projects for the given user inputs.

    Steps:
      1. Parse the raw skills input into a list.
      2. Score every project in the dataset.
      3. Drop projects with a score of zero (no overlap at all).
      4. Sort by score descending.
      5. Return the top MAX_RESULTS projects.
    """
    user_skills = parse_skills(skills_string)
    all_projects = load_all_projects()

    scored_projects = []

    for project in all_projects:
        score = score_single_project(
            project, user_skills, level, interest, time_availability
        )
        # Ignore projects with a score of 0 since they
        # have no meaningful overlap with the user's inputs.
        if score > 0:
            scored_projects.append({"project": project, "score": score})

    # Sort projects in descending order so the
    # most relevant recommendations appear first.
    scored_projects.sort(key=lambda item: item["score"], reverse=True)

    # Return only the project dicts, not the score metadata
    return [item["project"] for item in scored_projects[:MAX_RESULTS]]


def get_recommendations_with_match(skills_string, level, interest, time_availability):
    """
    Like get_recommendations, but each project includes a ``match`` breakdown.
    """
    user_skills = parse_skills(skills_string)
    all_projects = load_all_projects()
    scored_projects = []

    for project in all_projects:
        score = score_single_project(
            project, user_skills, level, interest, time_availability
        )
        if score > 0:
            entry = dict(project)
            entry["match"] = explain_project_match(
                project, user_skills, level, interest, time_availability
            )
            scored_projects.append({"project": entry, "score": score})

    scored_projects.sort(key=lambda item: item["score"], reverse=True)
    return [item["project"] for item in scored_projects[:MAX_RESULTS]]


def validate_recommendation_inputs(skills, level, interest, time_availability):
    """
    Validate all four required fields.
    Returns a list of error strings. An empty list means all inputs are valid.
    """
    errors = []

    if not skills or not skills.strip():
        errors.append("Please enter at least one skill.")

    if not level or not level.strip():
        errors.append("Please select an experience level.")

    if not interest or not interest.strip():
        errors.append("Please select an area of interest.")

    if not time_availability or not time_availability.strip():
        errors.append("Please select your time availability.")

    return errors
