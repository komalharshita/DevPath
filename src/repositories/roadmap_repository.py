# repositories/roadmap_repository.py
import json
import os
import threading

ROADMAPS_FILE = os.path.normpath(
    os.path.join(os.path.dirname(__file__), "..", "..", "data", "career_roadmaps.json")
)
_roadmaps_cache = None
_cache_lock = threading.Lock()


def load_raw_career_roadmaps():
    """Read and return all career roadmaps from JSON (cached after first read)."""
    global _roadmaps_cache
    if _roadmaps_cache is None:
        with _cache_lock:
            if _roadmaps_cache is None:
                with open(ROADMAPS_FILE, "r", encoding="utf-8") as handle:
                    _roadmaps_cache = json.load(handle)
    return _roadmaps_cache


def clear_cache():
    """Reset the in-memory raw career roadmaps cache."""
    global _roadmaps_cache
    with _cache_lock:
        _roadmaps_cache = None
