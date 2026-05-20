# utils/data_loader.py
# Handles all reading and lookup of project data from the JSON file.
# Manages skill counter persistence for tracking community usage.

import json
import os
from threading import Lock

# Build the path to projects.json relative to this file's location
DATA_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "projects.json")

# Path to skills counters data
SKILLS_COUNTERS_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "skills_counters.json")

# Thread lock to prevent concurrent writes to skills_counters.json
skills_counter_lock = Lock()


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


def load_skill_counters():
    """Read and return the skill counters from the JSON file."""
    with skills_counter_lock:
        with open(SKILLS_COUNTERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)


def save_skill_counters(counters):
    """Write skill counters to the JSON file."""
    with skills_counter_lock:
        with open(SKILLS_COUNTERS_FILE, "w", encoding="utf-8") as f:
            json.dump(counters, f, indent=2, ensure_ascii=False)


def increment_skill_counter(skill_label):
    """
    Increment the counter for a given skill label.
    Returns the updated counter value, or -1 if the skill is not found.
    """
    counters = load_skill_counters()
    
    # Normalize the skill label for case-insensitive lookup
    skill_key = None
    for key in counters.keys():
        if key.lower() == skill_label.lower():
            skill_key = key
            break
    
    if skill_key is None:
        return -1
    
    counters[skill_key] = counters[skill_key] + 1
    save_skill_counters(counters)
    
    return counters[skill_key]


def get_top_skills(count=5):
    """
    Get the top N skills by counter value.
    Returns a list of dicts with 'label' and 'counter' keys.
    """
    counters = load_skill_counters()
    
    # Convert to list of (label, count) tuples, sort by count descending
    sorted_skills = sorted(counters.items(), key=lambda x: x[1], reverse=True)
    
    # Return only the top N
    top_skills = sorted_skills[:count]
    
    return [{"label": label, "counter": count} for label, count in top_skills]


# Cache for loaded projects
_projects_cache = None


def clear_cache():
    """Reset the in-memory project cache."""
    global _projects_cache
    _projects_cache = None
