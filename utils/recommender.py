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


def parse_skills(skills_data):
    """
    Convert raw skills data into a deduplicated, normalized list.
    Supports both legacy comma-separated strings and newer JSON array formats
    (including objects with proficiency levels).
    """
    import json
    raw_skills = []

    # Attempt to parse as JSON first to support newer structured formats
    try:
        if isinstance(skills_data, str) and skills_data.strip().startswith('['):
            data = json.loads(skills_data)
            if isinstance(data, list):
                for item in data:
                    if isinstance(item, str):
                        raw_skills.append(item)
                    elif isinstance(item, dict):
                        # Extract skill name from objects (e.g., {"name": "Python", "level": "Expert"})
                        name = item.get("name") or item.get("skill")
                        if name:
                            raw_skills.append(str(name))
        else:
            # Fallback to legacy comma-separated string format
            raw_skills = [s.strip() for s in skills_data.split(",") if s.strip()]
    except (json.JSONDecodeError, AttributeError):
        # If JSON parsing fails or data is not a string, try basic split if possible
        if isinstance(skills_data, str):
            raw_skills = [s.strip() for s in skills_data.split(",") if s.strip()]

    normalized_skills = []
    seen_skills = set()

    for rs in raw_skills:
        # Normalize each skill name (case-insensitive deduplication)
        skill_norm = rs.strip().lower()
        if not skill_norm:
            continue

        # Resolve aliases (e.g., "js" -> "javascript")
        canonical = SKILL_ALIASES.get(skill_norm, skill_norm)

        # Check tracking set before adding to the final list
        if canonical not in seen_skills:
            normalized_skills.append(canonical)
            seen_skills.add(canonical)

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
    # Add weighted points based on the number of matching skills.
    # More overlapping skills result in a higher recommendation score.
    score += matched_skills * SCORING_WEIGHTS["skill"]

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
