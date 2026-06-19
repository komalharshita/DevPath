# services/learning_path_service.py
import re
import secrets

from repositories.learning_path_repository import save, get, update, exists, clear_all

# Maximum byte length accepted for a path_id to prevent abuse
_MAX_PATH_ID_LEN = 128

# Regex that path_id values must satisfy (alphanumeric + hyphens/underscores)
_PATH_ID_RE = re.compile(r"^[A-Za-z0-9_-]{1,128}$")


# ---------------------------------------------------------------------------
# Custom exception hierarchy
# ---------------------------------------------------------------------------

class LearningPathError(Exception):
    """Base class for all learning-path errors."""


class PathNotFoundError(LearningPathError):
    """Raised when a path_id does not exist in the store."""


class PathAlreadyExistsError(LearningPathError):
    """Raised when trying to create a path_id that is already registered."""


class AuthorizationError(LearningPathError):
    """Raised when the supplied token does not match the stored token."""


# ---------------------------------------------------------------------------
# Input validation helpers
# ---------------------------------------------------------------------------

def _validate_path_id(path_id: str) -> None:
    """Raise ValueError if path_id is not a safe, well-formed identifier."""
    if not isinstance(path_id, str) or not _PATH_ID_RE.match(path_id):
        raise ValueError(
            "path_id must be 1–128 characters and contain only "
            "letters, digits, hyphens, or underscores."
        )


def _validate_token(token: str) -> None:
    """Raise ValueError if token is not a non-empty string."""
    if not isinstance(token, str) or not token.strip():
        raise ValueError("token must be a non-empty string.")


def _validate_data(data: dict) -> None:
    """Raise ValueError if data is not a plain dict."""
    if not isinstance(data, dict):
        raise ValueError("data must be a JSON object (dict).")


def _tokens_equal(a: str, b: str) -> bool:
    """Compare two token strings in constant time to prevent timing attacks."""
    return secrets.compare_digest(a, b)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def create_learning_path(path_id: str, token: str, data: dict) -> None:
    """Register a new learning path."""
    _validate_path_id(path_id)
    _validate_token(token)
    _validate_data(data)

    if exists(path_id):
        raise PathAlreadyExistsError(
            f"A learning path with id '{path_id}' already exists."
        )

    save(path_id, token, data)


def get_learning_path(path_id: str, token: str) -> dict:
    """Return the data payload for a learning path."""
    _validate_path_id(path_id)
    _validate_token(token)

    stored = get(path_id)
    if not stored:
        raise PathNotFoundError(
            f"No learning path found with id '{path_id}'."
        )

    if not _tokens_equal(stored["token"], token):
        raise AuthorizationError(
            "The provided token does not match the owner token for this path."
        )

    return stored["data"]


def update_learning_path(path_id: str, token: str, data: dict) -> None:
    """Overwrite the data payload for an existing learning path."""
    _validate_path_id(path_id)
    _validate_token(token)
    _validate_data(data)

    stored = get(path_id)
    if not stored:
        raise PathNotFoundError(
            f"No learning path found with id '{path_id}'."
        )

    if not _tokens_equal(stored["token"], token):
        raise AuthorizationError(
            "The provided token does not match the owner token for this path."
        )

    update(path_id, data)


def path_exists(path_id: str) -> bool:
    """Return True if path_id is registered, False otherwise."""
    if not isinstance(path_id, str):
        return False
    return exists(path_id)
