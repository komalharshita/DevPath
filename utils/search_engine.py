# utils/search_engine.py
# Contains logic for advanced project filtering, fuzzy search, and custom sorting.

from utils.data_loader import load_all_projects
from utils.recommender import parse_skills, score_single_project


def search_projects(query_params):
    """
    Perform advanced filtering, fuzzy text search, and custom sorting on projects.

    query_params: dict containing optional search keys:
      - q: string (fuzzy text search across title, description, skills, tech stack)
      - skills: string (comma-separated skills, e.g. "python, javascript")
      - level: string (Beginner | Intermediate | Advanced)
      - interest: string (Web | Data | Education | Automation | Games etc.)
      - time: string (Low | Medium | High)
      - tech_stack: string (comma-separated tech stack items)
      - prerequisite_skills: string (comma-separated prerequisite skills)
      - min_hours: int/str (minimum estimated hours)
      - max_hours: int/str (maximum estimated hours)
      - sort_by: string (relevance | views | recommendations | hours_asc | hours_desc)

    Returns a list of project dicts that match all specified filters, sorted accordingly.
    """
    projects = load_all_projects()

    # 1. Parse and normalize inputs
    text_query = query_params.get("q", "").strip().lower()

    user_skills = parse_skills(query_params.get("skills", ""))
    level = query_params.get("level", "").strip()
    interest = query_params.get("interest", "").strip()
    time_avail = query_params.get("time", "").strip()

    # Clean and split multi-select arrays
    tech_stack_query = [
        t.strip().lower()
        for t in query_params.get("tech_stack", "").split(",")
        if t.strip()
    ]
    prereq_query = [
        p.strip().lower()
        for p in query_params.get("prerequisite_skills", "").split(",")
        if p.strip()
    ]

    try:
        min_hours = (
            int(query_params.get("min_hours"))
            if query_params.get("min_hours")
            else None
        )
    except (ValueError, TypeError):
        min_hours = None

    try:
        max_hours = (
            int(query_params.get("max_hours"))
            if query_params.get("max_hours")
            else None
        )
    except (ValueError, TypeError):
        max_hours = None

    sort_by = query_params.get("sort_by", "relevance").strip().lower()

    filtered_results = []

    for project in projects:
        # ---- Hard Filters ----

        # Level filter (case-insensitive, exact match if provided)
        if level and project.get("level", "").lower() != level.lower():
            continue

        # Interest filter (case-insensitive, exact match if provided)
        if interest and project.get("interest", "").lower() != interest.lower():
            continue

        # Time availability filter (case-insensitive, exact match if provided)
        if time_avail and project.get("time", "").lower() != time_avail.lower():
            continue

        # Tech stack filter: Project must contain at least one of the queried tech stack items
        if tech_stack_query:
            proj_tech = [t.lower() for t in project.get("tech_stack", [])]
            if not any(t in proj_tech for t in tech_stack_query):
                continue

        # Prerequisite skills filter: Project must contain at least one of the queried prerequisite skills
        if prereq_query:
            proj_prereq = [p.lower() for p in project.get("prerequisite_skills", [])]
            if not any(p in proj_prereq for p in prereq_query):
                continue

        # Estimated hours bounds
        proj_hours = project.get("estimated_hours", 0)
        if min_hours is not None and proj_hours < min_hours:
            continue
        if max_hours is not None and proj_hours > max_hours:
            continue

        # ---- Fuzzy Keyword Search ----
        # Matches against Title, Description, Skills, and Tech Stack
        if text_query:
            title = project.get("title", "").lower()
            desc = project.get("description", "").lower()
            terms = text_query.split()
            matched_text = True
            for term in terms:
                in_title = term in title
                in_desc = term in desc
                in_skills = any(term in s.lower() for s in project.get("skills", []))
                in_tech = any(term in ts.lower() for ts in project.get("tech_stack", []))
                if not (in_title or in_desc or in_skills or in_tech):
                    matched_text = False
                    break
            if not matched_text:
                continue

        # Calculate recommendation relevance score (soft matching based on skills & preferences)
        relevance_score = score_single_project(
            project,
            user_skills=user_skills,
            level=level if level else "",
            interest=interest if interest else "",
            time_availability=time_avail if time_avail else "",
        )

        filtered_results.append(
            {
                "project": project,
                "relevance_score": relevance_score,
                "views": project.get("views", 0),
                "recommendations": project.get("recommendations", 0),
                "hours": project.get("estimated_hours", 0),
            }
        )

    # 2. Sorting Logic
    if sort_by == "views":
        filtered_results.sort(key=lambda item: item["views"], reverse=True)
    elif sort_by == "recommendations":
        filtered_results.sort(key=lambda item: item["recommendations"], reverse=True)
    elif sort_by == "hours_asc":
        filtered_results.sort(key=lambda item: item["hours"])
    elif sort_by == "hours_desc":
        filtered_results.sort(key=lambda item: item["hours"], reverse=True)
    else:  # "relevance" (Default)
        # Sort by relevance score descending, secondary sort by views descending
        filtered_results.sort(
            key=lambda item: (item["relevance_score"], item["views"]), reverse=True
        )

    return [item["project"] for item in filtered_results]
