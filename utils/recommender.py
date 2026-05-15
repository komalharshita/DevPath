# utils/recommender.py
# Contains all recommendation logic: scoring and filtering projects.
# Kept separate from routing so it can be tested and extended independently.

from utils.data_loader import load_all_projects

# Maximum number of recommendations returned to the user
MAX_RESULTS = 3

# Scoring weights used by the recommendation engine.
# Higher weights mean that criterion has more influence
# on the final recommendation score.
WEIGHT_SKILL   = 3   # Skills are weighted highest because they best reflect project compatibility
WEIGHT_LEVEL   = 2   # Matching experience level helps avoid projects that are too easy or too difficult
WEIGHT_INTEREST = 2   # Interest alignment improves recommendation relevance
WEIGHT_TIME    = 1    # Time availability acts as a smaller tie-breaker factor


def parse_skills(skills_string):
    """
    Convert a raw comma-separated skills string into a clean lowercase list.
    Example: "Python, HTML, CSS" -> ["python", "html", "css"]
    """
    return [s.strip().lower() for s in skills_string.split(",") if s.strip()]


def score_single_project(project, user_skills, level, interest, time_availability):
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
