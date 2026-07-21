# utils/roadmap_comparer.py
# Load career roadmaps and compute side-by-side comparisons.

import json
import os
import threading

ROADMAPS_FILE = os.path.join(
    os.path.dirname(__file__), "..", "..", "data", "career_roadmaps.json"
)
_roadmaps_cache = None
_cache_lock = threading.Lock()

REQUIRED_FIELDS = [
    "id", "title", "description", "topics", "skills",
    "duration", "duration_weeks", "difficulty", "difficulty_score",
    "career_opportunities",
]


def _normalize(value):
    """Normalize a string for case-insensitive comparison."""
    return value.strip().lower()


def validate_roadmaps(roadmaps):
    """Validate career roadmap dataset integrity."""
    seen_ids = set()

    for roadmap in roadmaps:
        for field in REQUIRED_FIELDS:
            if field not in roadmap:
                raise ValueError(f"Missing required field: {field}")

        roadmap_id = roadmap["id"]
        if roadmap_id in seen_ids:
            raise ValueError(f"Duplicate roadmap ID found: {roadmap_id}")
        seen_ids.add(roadmap_id)

        if not isinstance(roadmap["topics"], list) or not roadmap["topics"]:
            raise ValueError(f"Roadmap '{roadmap_id}' must have at least one topic")

        if not isinstance(roadmap["skills"], list) or not roadmap["skills"]:
            raise ValueError(f"Roadmap '{roadmap_id}' must have at least one skill")


def load_all_career_roadmaps():
    """Read and return all career roadmaps from JSON (cached after first read)."""
    global _roadmaps_cache
    with _cache_lock:
        if _roadmaps_cache is None:
            with open(ROADMAPS_FILE, "r", encoding="utf-8") as handle:
                _roadmaps_cache = json.load(handle)
            validate_roadmaps(_roadmaps_cache)
    return _roadmaps_cache


def find_roadmap_by_id(roadmap_id):
    """Return the roadmap whose id matches, or None."""
    for roadmap in load_all_career_roadmaps():
        if roadmap.get("id") == roadmap_id:
            return roadmap
    return None


def _partition_lists(list_a, list_b):
    """Return (overlapping, unique_a, unique_b) using case-insensitive matching."""
    norm_b = {_normalize(item): item for item in list_b}
    norm_a = {_normalize(item): item for item in list_a}

    overlapping = []
    unique_a = []
    seen_overlap = set()

    for key, original in norm_a.items():
        if key in norm_b:
            if key not in seen_overlap:
                overlapping.append(original)
                seen_overlap.add(key)
        else:
            unique_a.append(original)

    unique_b = [
        original for key, original in norm_b.items() if key not in norm_a
    ]

    return overlapping, unique_a, unique_b


def compare_roadmaps(roadmap_id_a, roadmap_id_b):
    """
    Compare two career roadmaps and return structured comparison data.

    Returns None if either roadmap ID is invalid.
    """
    roadmap_a = find_roadmap_by_id(roadmap_id_a)
    roadmap_b = find_roadmap_by_id(roadmap_id_b)

    if not roadmap_a or not roadmap_b:
        return None

    if roadmap_id_a == roadmap_id_b:
        return {
            "error": "Please select two different roadmaps to compare.",
        }

    overlap_skills, unique_a_skills, unique_b_skills = _partition_lists(
        roadmap_a["skills"], roadmap_b["skills"]
    )
    overlap_topics, unique_a_topics, unique_b_topics = _partition_lists(
        roadmap_a["topics"], roadmap_b["topics"]
    )

    overlap_careers, unique_a_careers, unique_b_careers = _partition_lists(
        roadmap_a["career_opportunities"], roadmap_b["career_opportunities"]
    )

    max_duration = max(roadmap_a["duration_weeks"], roadmap_b["duration_weeks"], 1)
    max_difficulty = 5

    return {
        "roadmap_a": roadmap_a,
        "roadmap_b": roadmap_b,
        "overlapping_skills": overlap_skills,
        "unique_skills_a": unique_a_skills,
        "unique_skills_b": unique_b_skills,
        "overlapping_topics": overlap_topics,
        "unique_topics_a": unique_a_topics,
        "unique_topics_b": unique_b_topics,
        "overlapping_careers": overlap_careers,
        "unique_careers_a": unique_a_careers,
        "unique_careers_b": unique_b_careers,
        "summary": {
            "shared_skills_count": len(overlap_skills),
            "shared_topics_count": len(overlap_topics),
            "total_unique_skills": len(unique_a_skills) + len(unique_b_skills),
        },
        "metrics": {
            "duration_weeks": {
                "a": roadmap_a["duration_weeks"],
                "b": roadmap_b["duration_weeks"],
                "max": max_duration,
            },
            "difficulty_score": {
                "a": roadmap_a["difficulty_score"],
                "b": roadmap_b["difficulty_score"],
                "max": max_difficulty,
            },
            "topics_count": {
                "a": len(roadmap_a["topics"]),
                "b": len(roadmap_b["topics"]),
            },
            "skills_count": {
                "a": len(roadmap_a["skills"]),
                "b": len(roadmap_b["skills"]),
            },
            "career_count": {
                "a": len(roadmap_a["career_opportunities"]),
                "b": len(roadmap_b["career_opportunities"]),
            },
        },
    }


def clear_roadmap_cache():
    """Reset the in-memory roadmap cache (used in tests)."""
    global _roadmaps_cache
    with _cache_lock:
        _roadmaps_cache = None
