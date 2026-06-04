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

WEIGHT_SKILL = SCORING_WEIGHTS["skill"]
WEIGHT_LEVEL = SCORING_WEIGHTS["level"]
WEIGHT_INTEREST = SCORING_WEIGHTS["interest"]
WEIGHT_TIME = SCORING_WEIGHTS["time"]


# Common aliases and abbreviations for skills
# This improves recommendation accuracy by normalizing user input
SKILL_ALIASES = {
    "js": "javascript",
    "py": "python",
    "html5": "html",
    "css3": "css",
    "c++": "cpp",
    "web dev": ["javascript", "html", "css"]
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

    normalized_skills = []
    for skill in raw_skills:
        alias = SKILL_ALIASES.get(skill, skill)
        if isinstance(alias, list):
            normalized_skills.extend(alias)
        else:
            normalized_skills.append(alias)

    return normalized_skills

# -------------
def score_single_project(
        project, user_skills,
        level, interest, time_availability):
    """
    Calculate a numeric relevance score for one project.

    Each matching criterion adds points:
      - Skill coverage score: matched * WEIGHT_SKILL * coverage_ratio
      - Level match:          +2
      - Interest match:       +2
      - Time match:           +1

    coverage_ratio = matched_skills / total_project_skills
    This means a user covering 1 of 2 required skills scores less
    than a user covering both, even with the same raw match count.

    Returns a float score (0 means no match at all).
    """
    # Compare time availability, return results with the same time availibity or lower.
    TIME_AVAILABILITY = ['low', 'medium', 'high']
    time_availability_index =   TIME_AVAILABILITY.index(time_availability.strip().lower())
    valid_time = TIME_AVAILABILITY[ : time_availability_index + 1 ]
    
    score = 0

    # Compare user's skills against the project's required skills
    project_skills = [SKILL_ALIASES.get(s.lower(), s.lower()) for s in project.get("skills", [])]
    # Count how many user skills overlap with the
    # skills required by the current project.
    matched_skills = sum(1 for skill in user_skills if skill in project_skills)
    total_project_skills = len(project_skills)
    coverage_ratio = matched_skills / total_project_skills if total_project_skills > 0 else 0.0

    # Add weighted points based on the number of matching skills.
    # Skill coverage boosts score when more project skills are matched.
    score += matched_skills * SCORING_WEIGHTS["skill"] * coverage_ratio

    # Award points for each additional matching criterion
    if project.get("level", "").lower() == level.lower():
        score += SCORING_WEIGHTS["level"]

    if project.get("interest", "").lower() == interest.lower():
        score += SCORING_WEIGHTS["interest"]

    if project.get("time", "").lower() == time_availability.lower():
        score += SCORING_WEIGHTS["time"]

    if project.get("time", "").lower() in valid_time :
        return score
    return 0

# -----------
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


VALID_LEVELS = ["beginner", "intermediate", "advanced"]
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

    if not interest or not interest.strip():
        errors.append("Please select an area of interest.")

    if not time_availability or not time_availability.strip():
        errors.append("Please select your time availability.")
    elif time_availability.strip().lower() not in VALID_TIME_AVAILABILITY:
        errors.append("Invalid time availability. Choose Low, Medium, or High.")

    return errors
