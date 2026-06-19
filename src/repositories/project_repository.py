# repositories/project_repository.py
import json
import os
import threading

DATA_FILE = os.path.normpath(
    os.path.join(os.path.dirname(__file__), "..", "..", "data", "projects.json")
)

_projects_cache = None
_cache_lock = threading.Lock()


def load_raw_projects():
    """Read and return the raw list of projects from the JSON file.

    Results are cached in memory after the first read so subsequent calls
    do not hit the filesystem.
    """
    global _projects_cache
    if _projects_cache is None:
        with _cache_lock:
            if _projects_cache is None:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    _projects_cache = json.load(f)
    return _projects_cache


def find_project_by_id(project_id):
    """Return the raw project dictionary matching the ID, or None."""
    projects = load_raw_projects()
    for project in projects:
        if project.get("id") == project_id:
            return project
    return None


def clear_cache():
    """Reset the in-memory raw project cache."""
    global _projects_cache
    with _cache_lock:
        _projects_cache = None
