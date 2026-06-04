# utils/data_loader.py
# Handles all reading and lookup of project data from the JSON file.

import json
import os

# Build the path to projects.json relative to this file's location
DATA_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "projects.json")


def load_all_projects():
    """Read and return the full list of projects from the JSON file."""
    global _projects_cache
    if _projects_cache is None:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            _projects_cache = json.load(f)
    return _projects_cache


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

# Cache for loaded projects
_projects_cache = None


def clear_cache():
    """Reset the in-memory project cache."""
    global _projects_cache
    _projects_cache = None
