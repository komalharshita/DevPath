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
    Convert a raw skills input into a list of skill objects.
    Supports both new JSON format and legacy comma-separated strings.

    New format: '[{"name": "Python", "level": "Advanced"}]'
    Legacy format: "Python, JavaScript"
    """
    import json
    
    # Try parsing as JSON first (new format)
    try:
        data = json.loads(skills_string)
        if isinstance(data, list):
            return [
                {
                    "name": SKILL_ALIASES.get(s["name"].strip().lower(), s["name"].strip().lower()),
                    "level": s.get("level", "Intermediate")
                }
                for s in data
                if s.get("name")
            ]
    except (json.JSONDecodeError, TypeError, KeyError):
        pass

    # Fallback to legacy comma-separated string
    raw_skills = [
        s.strip().lower()
        for s in skills_string.split(",")
        if s.strip()
    ]

    normalized_skills = [
        {"name": SKILL_ALIASES.get(skill, skill), "level": "Intermediate"}
        for skill in raw_skills
    ]

    return normalized_skills


def score_single_project(
        project, user_skills,
        level, interest, time_availability):
    """
    Calculate a numeric relevance score for one project.

    user_skills is a list of dicts: [{"name": "python", "level": "Advanced"}, ...]

    Scoring:
      - Base skill match:     +3
      - Proficiency bonus:    +2 (matches project level) or +1 (near match)
      - Experience match:     +2 (user overall level match)
      - Interest match:       +2
      - Time match:           +1
    """
    # Compare time availability, return results with the same time availibity or lower.
    TIME_AVAILABILITY = ['low', 'medium', 'high']
    time_availability_index = TIME_AVAILABILITY.index(time_availability.strip().lower())
    valid_time = TIME_AVAILABILITY[ : time_availability_index + 1 ]
    
    score = 0

    # Project skills for matching
    project_skills = [SKILL_ALIASES.get(s.lower(), s.lower()) for s in project.get("skills", [])]
    project_level = project.get("level", "Intermediate").lower()

    # Match each user skill
    for u_skill in user_skills:
        u_name = u_skill["name"]
        u_prof = u_skill["level"].lower()
        
        if u_name in project_skills:
            # Base match
            score += SCORING_WEIGHTS["skill"]
            
            # Proficiency steering
            # Reward matching the user's specific skill proficiency with the project complexity
            if u_prof == project_level:
                score += 2 # Perfect alignment
            elif (u_prof == "advanced" and project_level == "intermediate") or \
                 (u_prof == "intermediate" and project_level == "beginner"):
                score += 1 # Overqualified/Growth alignment

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
