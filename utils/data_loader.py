# utils/data_loader.py
# Handles all reading and lookup of project data from the JSON file.

import json
import os

# Build the path to projects.json relative to this file's location
DATA_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "projects.json")


def load_all_projects():
    """Read and return the full list of projects from the JSON file."""
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def find_project_by_id(project_id):
    """
    Return the project dict whose 'id' matches the given integer.
    Returns None if no match is found.
    """
    for project in load_all_projects():
        if project.get("id") == project_id:
            return project
    return None

# Cache for loaded projects
_projects_cache = None


def clear_cache():
    """Reset the in-memory project cache."""
    global _projects_cache
    _projects_cache = None
