# utils/data_loader.py
# Compatibility shim forwarding to services.project_service and repositories.project_repository
from repositories.project_repository import DATA_FILE
from services.project_service import (
    load_all_projects,
    find_project_by_id,
    get_available_levels,
    get_project_stats,
    clear_cache,
    validate_projects,
)
