# utils/roadmap_comparer.py
# Compatibility shim forwarding to services.roadmap_service and repositories.roadmap_repository
from repositories.roadmap_repository import ROADMAPS_FILE
from services.roadmap_service import (
    load_all_career_roadmaps,
    find_roadmap_by_id,
    compare_roadmaps,
    validate_roadmaps,
    clear_cache as clear_roadmap_cache,
)
