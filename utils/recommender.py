# utils/recommender.py
# Contains all recommendation logic: scoring and filtering projects.
# Kept separate from routing so it can be tested and extended independently.

from utils.data_loader import load_all_projects

# Maximum number of recommendations returned to the user
MAX_RESULTS = 3

# Scoring weights used by the recommendation engine.
# Higher weights mean that criterion has more influence
# on the final recommendation score.
SCORING_WEIGHTS = {
    "skill":    3,
    "level":    2,
    "interest": 2,
    "time":     1,
}


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

    Returns the total weighted relevance score for the project.
    Projects with zero skill overlap are filtered later
    inside get_recommendations().
    """
    score = 0

    # Compare user's skills against the project's required skills
    project_skills = [
    SKILL_ALIASES.get(s.lower(), s.lower())
    for s in project.get("skills", [])
]

    # Count how many user skills overlap with the
    # skills required by the current project.
    matched_skills = sum(1 for skill in user_skills if skill in project_skills)

    # Calculate skill score separately so we can check it later
    skill_score = matched_skills * SCORING_WEIGHTS["skill"]

    # Add weighted points based on the number of matching skills.
    score += skill_score

    # Award points for each additional matching criterion
    if project.get("level", "").lower() == level.lower():
        score += SCORING_WEIGHTS["level"]

    if project.get("interest", "").lower() == interest.lower():
        score += SCORING_WEIGHTS["interest"]

    if project.get("time", "").lower() == time_availability.lower():
        score += SCORING_WEIGHTS["time"]

    # Return both total score and skill score as a tuple
    return score


def get_recommendations(skills_string, level, interest, time_availability):
    """
    Return the top N recommended projects for the given user inputs.

    Steps:
      1. Parse the raw skills input into a list.
      2. Score every project in the dataset.
      3. Drop projects with zero skill overlap — even if level
         or interest matches, a project with no skill match
         is not relevant to the user.
      4. Sort by score descending.
      5. Return the top MAX_RESULTS projects.
    """
    user_skills = parse_skills(skills_string)
    all_projects = load_all_projects()

    scored_projects = []

    for project in all_projects:
        score = score_single_project(project, user_skills, level, interest, time_availability)

        # Calculate skill score separately to check for zero skill overlap.
        # Projects with no skill match are rejected even if level or
        # interest matches, since they are not relevant to the user.
        project_skills = [ SKILL_ALIASES.get(s.lower(), s.lower()) for s in project.get("skills", []) ]
        skill_score = sum(1 for skill in user_skills if skill in project_skills) * SCORING_WEIGHTS["skill"]

        if skill_score == 0:
            continue


        scored_projects.append({"project": project, "score": score})

    # Sort projects in descending order so the
    # most relevant recommendations appear first.
    scored_projects.sort(key=lambda item: item["score"], reverse=True)

    # Return only the project dicts, not the score metadata
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