# utils/data_loader.py
# utils/data_loader.py
import json
import os
import threading
import logging
from pathlib import Path

from utils.url_validator import is_valid_url, parse_resource
from models import Project

logger = logging.getLogger("devpath.data_loader")


def validate_projects(projects):
    """
    Validate project dataset integrity.

    Checks for:
    - Duplicate project IDs
    - Duplicate project titles (case-insensitive)
    - Missing required fields
    - Empty required string fields
    - Malformed resource URLs (logs a warning, does not raise)

    Raises:
        ValueError: If any structural validation rule is violated.
    """
    seen_ids = set()
    seen_titles = set()

    required_fields = [
        "id", "title", "skills", "level", "interest", "time",
        "description", "features", "tech_stack", "roadmap",
        "resources", "starter_code"
    ]

    for project in projects:
        # Required fields
        for field in required_fields:
            if field not in project:
                raise ValueError(f"Missing required field: {field}")

            if isinstance(project[field], str) and not project[field].strip():
                raise ValueError(
                    f"Empty value for field '{field}' in project '{project.get('title', 'Unknown')}'"
                )

        # Duplicate IDs
        project_id = project["id"]
        if project_id in seen_ids:
            raise ValueError(f"Duplicate project ID found: {project_id}")
        seen_ids.add(project_id)

        # Duplicate Titles
        title = " ".join(project["title"].split()).lower()
        if title in seen_titles:
            raise ValueError(f"Duplicate project title found: {project['title']}")
        seen_titles.add(title)

        # Resource URL format validation — warn, do not raise
        # Broken URLs in production are logged so they can be fixed in the
        # data file without crashing the application.
        for raw in project.get("resources", []):
            parsed = parse_resource(raw)
            url = parsed.get("url", "")
            if url and not is_valid_url(url):
                logger.warning(
                    "Malformed resource URL in project '%s' (id=%s): %r",
                    project.get("title", "Unknown"),
                    project_id,
                    url,
                )


def load_all_projects():
    """Read and return the full list of projects from the database."""
    projects = Project.query.all()
    return [p.to_dict() for p in projects]

def get_available_levels():
    """Return all unique project levels."""
    projects = load_all_projects()
    return sorted({p["level"] for p in projects})

def get_available_interests():
    """Return all unique project interests."""
    projects = load_all_projects()
    return sorted({p["interest"] for p in projects if "interest" in p})
def find_project_by_id(project_id):
    """Return the project whose 'id' matches project_id, or None."""
    from models import db
    p = db.session.get(Project, project_id)
    return p.to_dict() if p else None


def get_project_stats():
    """Return total_projects, unique_skills, and beginner_friendly counts."""
    projects = load_all_projects()

    all_skills = set()
    beginner_friendly = 0
    for p in projects:
        for s in p.get("skills", []):
            all_skills.add(s)
        if p.get("level") == "Beginner":
            beginner_friendly += 1

    return {
        "total_projects": len(projects),
        "unique_skills": len(all_skills),
        "beginner_friendly": beginner_friendly,
    }

def clear_cache():
    """Reset the in-memory project cache (used in tests)."""
    pass
