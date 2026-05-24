# utils/data_loader.py
# Handles all reading and lookup of project data from the JSON file.

import json
import os
import copy

# Build the path to projects.json relative to this file's location
DATA_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "projects.json")

# Module-level project cache and tracking states
_projects_cache = None
_read_count = 0


def load_all_projects():
    """
    Read and return the full list of projects from the JSON file.
    Returns a deep copy of the cache to prevent callers from mutating the state.
    """
    global _projects_cache, _read_count
    if _projects_cache is None:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            _projects_cache = json.load(f)
            _read_count += 1
    return copy.deepcopy(_projects_cache)


def find_project_by_id(project_id):
    """
    Return the project dict whose 'id' matches the given integer.
    Returns None if no match is found.
    """
    for project in load_all_projects():
        if project.get("id") == project_id:
            return project
    return None

def get_project_stats():
    """
    Calculate and return statistics about the projects.
    Returns: { total_projects, unique_skills, beginner_friendly }
    """
    projects = load_all_projects()
    total_projects = len(projects)

    # Collect all unique skills
    all_skills = set()
    for p in projects:
        for s in p.get("skills", []):
            all_skills.add(s)
    unique_skills = len(all_skills)

    # Count beginner projects
    beginner_friendly = len([p for p in projects if p.get("level") == "Beginner"])

    return {
        "total_projects": total_projects,
        "unique_skills": unique_skills,
        "beginner_friendly": beginner_friendly
    }


def get_read_count():
    """Return the total number of times projects.json was read from disk."""
    global _read_count
    return _read_count


def clear_cache():
    """Reset the in-memory project cache and reset read tracking."""
    global _projects_cache, _read_count
    _projects_cache = None
    _read_count = 0
