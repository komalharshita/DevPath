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

# Curated trending skills per interest area.
# Shown as a fallback when the user already matches most dataset projects
# and no project-based skill gap can be computed.
TRENDING_SKILLS_BY_INTEREST = {
    "games": ["Unity", "C#", "Godot", "Lua", "Pygame", "OpenGL", "Unreal Engine"],
    "web": ["TypeScript", "GraphQL", "Docker", "Redis", "Kubernetes", "Tailwind CSS", "Vite"],
    "data": ["Apache Spark", "Scala", "R", "Airflow", "dbt", "Tableau", "Julia"],
    "automation": ["Ansible", "Terraform", "Bash", "Jenkins", "Prometheus", "Grafana"],
    "education": ["TypeScript", "React", "PostgreSQL", "Docker", "GraphQL"],
    "default": ["TypeScript", "Docker", "Kubernetes", "GraphQL", "Redis", "Terraform", "Rust"],
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


def _get_skill_matched_projects(skills_string, level, interest, time_availability):
    """
    Return projects where the user has at least one matching skill and the project
    passes the time filter. Used by get_skill_gap to find newly unlocked projects.
    """
    user_skills = parse_skills(skills_string)
    all_projects = load_all_projects()
    matched = []
    for project in all_projects:
        project_skills = [SKILL_ALIASES.get(s.lower(), s.lower()) for s in project.get("skills", [])]
        if any(skill in project_skills for skill in user_skills):
            if score_single_project(project, user_skills, level, interest, time_availability) > 0:
                matched.append(project)
    return matched


def _count_skill_matched_projects(skills_string, level, interest, time_availability):
    """Thin wrapper used by tests and legacy callers."""
    return len(_get_skill_matched_projects(skills_string, level, interest, time_availability))


def _project_based_gaps(skills_string, level, interest, time_availability):
    """
    Core gap computation: finds skills that unlock new project matches.
    Returns a deduplicated list — each project assigned to only the top skill
    that unlocks it, so every entry shows a distinct set of projects.
    """
    user_skills = parse_skills(skills_string)
    base_projects = _get_skill_matched_projects(skills_string, level, interest, time_availability)
    base_ids = {p["id"] for p in base_projects}

    all_projects = load_all_projects()
    seen_normalized = set()
    candidates = []
    for project in all_projects:
        for skill in project.get("skills", []):
            normalized = SKILL_ALIASES.get(skill.lower(), skill.lower())
            if normalized not in user_skills and normalized not in seen_normalized:
                seen_normalized.add(normalized)
                candidates.append(skill)

    raw_gaps = []
    for skill in candidates:
        extended = skills_string + ", " + skill
        new_projects = _get_skill_matched_projects(extended, level, interest, time_availability)
        unlocked = [p for p in new_projects if p["id"] not in base_ids]
        if unlocked:
            raw_gaps.append({"skill": skill, "unlocked": unlocked})

    raw_gaps.sort(key=lambda x: len(x["unlocked"]), reverse=True)

    assigned_ids = set()
    gaps = []
    for entry in raw_gaps:
        exclusive = [p for p in entry["unlocked"] if p["id"] not in assigned_ids]
        if exclusive:
            for p in exclusive:
                assigned_ids.add(p["id"])
            gaps.append({
                "skill": entry["skill"],
                "unlocks": len(exclusive),
                "projects": [{"id": p["id"], "title": p["title"]} for p in exclusive],
                "trending": False,
            })
        if len(gaps) == 8:
            break

    return gaps


def get_skill_gap(skills_string, level, interest, time_availability):
    """
    Return up to 8 skill gap suggestions.

    First tries to find skills that unlock real project matches in the dataset
    (project-based gaps). When a user already has broad skills and matches most
    projects, that list will be short or empty — in that case, the result is
    padded with curated trending skills for the chosen interest area so the
    user always gets actionable learning suggestions.

    Each entry:
        {"skill": str, "unlocks": int, "projects": [...], "trending": bool}
    trending=True entries have no associated projects (industry suggestions only).
    """
    gaps = _project_based_gaps(skills_string, level, interest, time_availability)

    if len(gaps) < 4:
        user_skills = parse_skills(skills_string)
        already_suggested = {SKILL_ALIASES.get(g["skill"].lower(), g["skill"].lower()) for g in gaps}

        interest_key = interest.strip().lower() if interest else "default"
        trending_pool = (
            TRENDING_SKILLS_BY_INTEREST.get(interest_key)
            or TRENDING_SKILLS_BY_INTEREST["default"]
        )

        for skill in trending_pool:
            normalized = SKILL_ALIASES.get(skill.lower(), skill.lower())
            if normalized not in user_skills and normalized not in already_suggested:
                already_suggested.add(normalized)
                gaps.append({
                    "skill": skill,
                    "unlocks": 0,
                    "projects": [],
                    "trending": True,
                })
            if len(gaps) == 8:
                break

    return gaps


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
