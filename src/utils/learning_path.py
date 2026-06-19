# utils/learning_path.py
# Compatibility shim forwarding to services.learning_path_service and repositories.learning_path_repository
from repositories.learning_path_repository import clear_all as _clear_all
from services.learning_path_service import (
    create_learning_path,
    get_learning_path,
    update_learning_path,
    path_exists,
    LearningPathError,
    PathNotFoundError,
    PathAlreadyExistsError,
    AuthorizationError,
)
