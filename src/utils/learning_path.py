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
# Storage is backed by the database (the ``LearningPath`` SQLAlchemy model)
# so paths survive application restarts, cold starts, and serverless function
# recycling, and are consistent across concurrent instances.  Only a salted
# SHA-256 hash of the owner token is persisted - the raw token is never
# stored, so a leaked database does not expose bearer secrets.
#
# Public surface:
#   create_learning_path(path_id, token, data)  -> None   (raises on conflict)
#   get_learning_path(path_id, token)           -> dict   (raises on auth fail)
#   update_learning_path(path_id, token, data)  -> None   (raises on auth fail)
#   path_exists(path_id)                        -> bool
#   cleanup_expired_paths([max_age_seconds])    -> int    (deleted row count)
#   _clear_all()                                -> None   (test helper only)
#
# Error types:
#   PathNotFoundError    – path_id does not exist
#   PathAlreadyExistsError – path_id is already registered (on create)
#   AuthorizationError   – token does not match the stored token

import hashlib
import re
import secrets
from datetime import datetime, timedelta, timezone

from models import db, LearningPath

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Maximum byte length accepted for a path_id to prevent abuse
_MAX_PATH_ID_LEN = 128

# Regex that path_id values must satisfy (alphanumeric + hyphens/underscores)
_PATH_ID_RE = re.compile(r"^[A-Za-z0-9_-]{1,128}$")

# Abandoned paths are purged after this many seconds without activity.  Paths
# that are actively updated never expire; this only cleans up paths whose
# owners stopped using them.
_PATH_TTL_SECONDS = 30 * 24 * 60 * 60  # 30 days


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


# ---------------------------------------------------------------------------
# Token hashing helpers
# ---------------------------------------------------------------------------

def _hash_token(token: str) -> str:
    """Return a salted SHA-256 hash of ``token``.

    The raw token is never stored; only ``"<salt>$<hex-digest>"`` is kept.
    """
    salt = secrets.token_hex(16)
    digest = hashlib.sha256((salt + token).encode("utf-8")).hexdigest()
    return f"{salt}${digest}"


def _verify_token(stored_hash: str, token: str) -> bool:
    """Verify ``token`` against a stored ``"<salt>$<digest>"`` hash.

    Comparison uses ``secrets.compare_digest`` (constant time) on the two
    equal-length hex digests.
    """
    try:
        salt, digest = stored_hash.split("$", 1)
    except (ValueError, AttributeError):
        return False
    candidate = hashlib.sha256((salt + token).encode("utf-8")).hexdigest()
    return secrets.compare_digest(candidate, digest)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def create_learning_path(path_id: str, token: str, data: dict) -> None:
    """Register a new learning path.

    Associates ``path_id`` with a hash of ``token`` and stores the initial
    ``data`` payload.  The caller is responsible for generating a
    cryptographically random token (e.g. ``secrets.token_urlsafe(32)``)
    before calling this function.

    Raises:
        ValueError             – if any argument fails basic validation.
        PathAlreadyExistsError – if path_id is already registered.
    """
    _validate_path_id(path_id)
    _validate_token(token)
    _validate_data(data)

    if db.session.get(LearningPath, path_id) is not None:
        raise PathAlreadyExistsError(
            f"A learning path with id '{path_id}' already exists."
        )

    path = LearningPath(
        path_id=path_id,
        token_hash=_hash_token(token),
        data=dict(data),
    )
    db.session.add(path)
    db.session.commit()

    # Opportunistically purge abandoned paths on write activity.
    cleanup_expired_paths()


def get_learning_path(path_id: str, token: str) -> dict:
    """Return the data payload for a learning path.

    Raises:
        ValueError         – if any argument fails basic validation.
        PathNotFoundError  – if path_id does not exist.
        AuthorizationError – if the token does not match.
    """
    _validate_path_id(path_id)
    _validate_token(token)

    path = db.session.get(LearningPath, path_id)
    if path is None:
        raise PathNotFoundError(
            f"No learning path found with id '{path_id}'."
        )

    if not _verify_token(path.token_hash, token):
        raise AuthorizationError(
            "The provided token does not match the owner token for this path."
        )

    # Return a copy so callers cannot mutate the stored state directly
    return dict(path.data or {})


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

    path = db.session.get(LearningPath, path_id)
    if path is None:
        raise PathNotFoundError(
            f"No learning path found with id '{path_id}'."
        )

    if not _verify_token(path.token_hash, token):
        raise AuthorizationError(
            "The provided token does not match the owner token for this path."
        )

    path.data = dict(data)
    db.session.commit()


def path_exists(path_id: str) -> bool:
    """Return True if path_id is registered, False otherwise.

    Does not require a token; existence is not considered sensitive because
    path_ids are meant to be opaque and unguessable (UUID-like) values.
    """
    if not isinstance(path_id, str):
        return False
    return db.session.get(LearningPath, path_id) is not None


def cleanup_expired_paths(max_age_seconds: int = _PATH_TTL_SECONDS) -> int:
    """Delete learning paths that have not been touched in ``max_age_seconds``.

    Returns the number of rows deleted.  Safe to call periodically (e.g. on
    write activity or from a cron/interval job); active paths are unaffected
    because their ``updated_at`` timestamp is refreshed on every update.
    """
    cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(
        seconds=max_age_seconds
    )
    deleted = LearningPath.query.filter(LearningPath.updated_at < cutoff).delete()
    if deleted:
        db.session.commit()
    return deleted


def _clear_all() -> None:
    """Remove all stored paths.

    This function exists solely for test isolation.  It must not be called
    from application code.
    """
    LearningPath.query.delete()
    db.session.commit()
