import json
import os
import threading

DATA_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "projects.json")

_projects_cache = None
_cache_lock = threading.Lock()


def load_all_projects():
    """Read and return the full list of projects from the JSON file.

    Results are cached in memory after the first read so subsequent calls
    do not hit the filesystem.
    """
    global _projects_cache
    if _projects_cache is not None:
        return _projects_cache
    with _cache_lock:
        if _projects_cache is None:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                _projects_cache = json.load(f)
    return _projects_cache


def find_project_by_id(project_id):
    """Return the project whose 'id' matches project_id, or None."""
    for project in load_all_projects():
        if project.get("id") == project_id:
            return project
    return None


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
    global _projects_cache
    with _cache_lock:
        _projects_cache = None
