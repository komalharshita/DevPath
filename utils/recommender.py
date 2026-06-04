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
    Convert a skills string into a normalized list of dicts.
    Handles both legacy comma-separated strings and new JSON proficiency objects.
    """
    import json
    
    try:
        # Try to parse as JSON (new format: [{"name": "Python", "level": "Beginner"}])
        skills_data = json.loads(skills_string)
        if isinstance(skills_data, list):
            return [{
                "name": SKILL_ALIASES.get(item["name"].lower(), item["name"].lower()),
                "level": item.get("level", "intermediate").lower()
            } for item in skills_data if isinstance(item, dict) and item.get("name")]
    except (json.JSONDecodeError, TypeError):
        pass

    # Fallback for legacy format: "JS, HTML5, CSS3" -> [{"name": "javascript", "level": "intermediate"}, ...]
    raw_skills = [
        s.strip().lower()
        for s in skills_string.split(",")
        if s.strip()
    ]

    return [
        {"name": SKILL_ALIASES.get(skill, skill), "level": "intermediate"}
        for skill in raw_skills
    ]


def score_single_project(
        project, user_skills,
        level, interest, time_availability):
    """
    Calculate a numeric relevance score for one project.

    Weights are adjusted based on skill-specific proficiency:
      - Skill match: +3 (base)
      - Proficiency match bonus: +1
      - Close match bonus (user > project): +0.5
    """
    # Compare time availability, return results with the same time availibity or lower.
    TIME_AVAILABILITY = ['low', 'medium', 'high']
    time_availability_index =   TIME_AVAILABILITY.index(time_availability.strip().lower())
    valid_time = TIME_AVAILABILITY[ : time_availability_index + 1 ]
    
    score = 0

    # Project required skills (normalized)
    project_skills = [SKILL_ALIASES.get(s.lower(), s.lower()) for s in project.get("skills", [])]
    project_level = project.get("level", "beginner").lower()

    # Score each user skill against project requirements
    for u_skill in user_skills:
        # Handle both list of strings (legacy/tests) and list of dicts (new)
        if isinstance(u_skill, dict):
            u_name = u_skill.get("name", "")
            u_level = u_skill.get("level", "intermediate").lower()
        else:
            u_name = u_skill
            u_level = "intermediate"

        if not u_name:
            continue
            
        u_name = SKILL_ALIASES.get(u_name.lower(), u_name.lower())

        if u_name in project_skills:
            # Base match points
            points = SCORING_WEIGHTS["skill"]

            # Adjust points based on proficiency match with project level
            if u_level == project_level:
                points += 1  # Perfect match
            elif (u_level == "advanced" and project_level == "intermediate") or \
                 (u_level == "intermediate" and project_level == "beginner"):
                points += 0.5  # User over-qualified is still a good match

            score += points

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
