# utils/learning_path.py
# Server-side storage and ownership verification for user learning paths.
#
# Learning paths are identified by a user-supplied ``path_id`` (an opaque
# string chosen by the client, typically a UUID generated in the browser).
# On the first write the caller must also provide a ``token`` that will be
# permanently associated with that path_id.  Every subsequent read or write
# must present the same token; requests with a missing or wrong token are
# rejected with a 403 status before any data is returned or modified.
#
# Storage is intentionally in-memory so the module has no external
# dependencies beyond the Python standard library.  Data does not survive
# an application restart, which is acceptable for this project's scope and
# is clearly documented in the API contract.
#
# Public surface:
#   create_learning_path(path_id, token, data)  -> None   (raises on conflict)
#   get_learning_path(path_id, token)           -> dict   (raises on auth fail)
#   update_learning_path(path_id, token, data)  -> None   (raises on auth fail)
#   path_exists(path_id)                        -> bool
#   _clear_all()                                -> None   (test helper only)
#
# Error types:
#   PathNotFoundError    – path_id does not exist
#   PathAlreadyExistsError – path_id is already registered (on create)
#   AuthorizationError   – token does not match the stored token

import re
import secrets

# ---------------------------------------------------------------------------
# Module-level storage
# ---------------------------------------------------------------------------

# Map of path_id -> {"token": str, "data": dict}
_store: dict = {}

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
    """Register a new learning path.

    Associates ``path_id`` with ``token`` and stores the initial ``data``
    payload.  The caller is responsible for generating a cryptographically
    random token (e.g. ``secrets.token_urlsafe(32)``) before calling this
    function.

    Raises:
        ValueError             – if any argument fails basic validation.
        PathAlreadyExistsError – if path_id is already registered.
    """
    _validate_path_id(path_id)
    _validate_token(token)
    _validate_data(data)

    if path_id in _store:
        raise PathAlreadyExistsError(
            f"A learning path with id '{path_id}' already exists."
        )

    _store[path_id] = {"token": token, "data": dict(data)}


def get_learning_path(path_id: str, token: str) -> dict:
    """Return the data payload for a learning path.

    Raises:
        ValueError         – if any argument fails basic validation.
        PathNotFoundError  – if path_id does not exist.
        AuthorizationError – if the token does not match.
    """
    _validate_path_id(path_id)
    _validate_token(token)

    if path_id not in _store:
        raise PathNotFoundError(
            f"No learning path found with id '{path_id}'."
        )

    stored = _store[path_id]
    if not _tokens_equal(stored["token"], token):
        raise AuthorizationError(
            "The provided token does not match the owner token for this path."
        )

    # Return a copy so callers cannot mutate the stored state directly
    return dict(stored["data"])


def update_learning_path(path_id: str, token: str, data: dict) -> None:
    """Overwrite the data payload for an existing learning path.

    The token must match the token supplied when the path was created.

    Raises:
        ValueError         – if any argument fails basic validation.
        PathNotFoundError  – if path_id does not exist.
        AuthorizationError – if the token does not match.
    """
    _validate_path_id(path_id)
    _validate_token(token)
    _validate_data(data)

    if path_id not in _store:
        raise PathNotFoundError(
            f"No learning path found with id '{path_id}'."
        )

    stored = _store[path_id]
    if not _tokens_equal(stored["token"], token):
        raise AuthorizationError(
            "The provided token does not match the owner token for this path."
        )

    stored["data"] = dict(data)


def path_exists(path_id: str) -> bool:
    """Return True if path_id is registered, False otherwise.

    Does not require a token; existence is not considered sensitive because
    path_ids are meant to be opaque and unguessable (UUID-like) values.
    """
    if not isinstance(path_id, str):
        return False
    return path_id in _store


def _clear_all() -> None:
    """Remove all stored paths.

    This function exists solely for test isolation.  It must not be called
    from application code.
    """
    _store.clear()
