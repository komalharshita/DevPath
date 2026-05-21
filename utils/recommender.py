# utils/recommender.py
# Contains all recommendation logic: scoring and filtering projects.
# Kept separate from routing so it can be tested and extended independently.

from utils.data_loader import load_all_projects

# Maximum number of recommendations returned to the user
MAX_RESULTS = 3

# Minimum score required for a project
# to be considered relevant enough for recommendation.
MIN_SCORE_THRESHOLD = 4

# Scoring weights used by the recommendation engine.
# Higher weights mean that criterion has more influence
# on the final recommendation score.
SCORING_WEIGHTS = {
    "skill": 3,
    "level": 2,
    "interest": 4,
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
    "ml": "machine learning",
    "ai": "artificial intelligence"
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
        project,
        user_skills,
        level,
        interest,
        time_availability):
    """
    Calculate a numeric relevance score for one project.

    Scoring criteria:
      - Matching skills
      - Matching level
      - Matching interest
      - Matching time availability

    Returns:
        Integer relevance score.
        Returns 0 immediately if the interest category does not match.
    """

    # Normalize project fields
    project_interest = project.get("interest", "").lower()
    project_level = project.get("level", "").lower()
    project_time = project.get("time", "").lower()

    # Strict interest filtering
    # Prevent unrelated category recommendations
    if project_interest != interest.lower():
        return 0

    score = 0

    # Compare user's skills against project skills
    project_skills = [
        s.lower()
        for s in project.get("skills", [])
    ]

    matched_skills = sum(
        1 for skill in user_skills
        if skill in project_skills
    )

    # Add weighted skill score
    score += matched_skills * SCORING_WEIGHTS["skill"]

    # Add score for matching level
    if project_level == level.lower():
        score += SCORING_WEIGHTS["level"]

    # Add score for matching interest
    score += SCORING_WEIGHTS["interest"]

    # Add score for matching time availability
    if project_time == time_availability.lower():
        score += SCORING_WEIGHTS["time"]

    return score


def get_recommendations(
        skills_string,
        level,
        interest,
        time_availability):
    """
    Return the top recommended projects for the given user inputs.

    Steps:
      1. Parse user skills.
      2. Score all projects.
      3. Remove weak/irrelevant matches.
      4. Sort by highest score.
      5. Return top MAX_RESULTS projects.
    """

    user_skills = parse_skills(skills_string)
    all_projects = load_all_projects()

    scored_projects = []

    for project in all_projects:

        score = score_single_project(
            project,
            user_skills,
            level,
            interest,
            time_availability
        )

        # Ignore weak matches
        if score >= MIN_SCORE_THRESHOLD:
            scored_projects.append({
                "project": project,
                "score": score
            })

    # Sort projects by descending score
    scored_projects.sort(
        key=lambda item: item["score"],
        reverse=True
    )

    # Return only project data
    return [
        item["project"]
        for item in scored_projects[:MAX_RESULTS]
    ]


def validate_recommendation_inputs(
        skills,
        level,
        interest,
        time_availability):
    """
    Validate all required recommendation inputs.

    Returns:
        List of validation error messages.
        Empty list means all inputs are valid.
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