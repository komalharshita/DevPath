# repositories/learning_path_repository.py
import threading

# Map of path_id -> {"token": str, "data": dict}
_store = {}
_store_lock = threading.Lock()


def save(path_id, token, data):
    """Save a new learning path mapping path_id to token and data."""
    with _store_lock:
        _store[path_id] = {"token": token, "data": dict(data)}


def get(path_id):
    """Retrieve learning path details by path_id.

    Returns the dictionary containing 'token' and 'data', or None if not found.
    """
    with _store_lock:
        stored = _store.get(path_id)
        if stored:
            # Return a shallow copy of the container dictionary and the data dict
            # to prevent direct mutation of the internal store state.
            return {"token": stored["token"], "data": dict(stored["data"])}
        return None


def update(path_id, data):
    """Update the data payload of an existing learning path."""
    with _store_lock:
        if path_id in _store:
            _store[path_id]["data"] = dict(data)


def exists(path_id):
    """Return True if path_id exists in the store, False otherwise."""
    with _store_lock:
        return path_id in _store


def clear_all():
    """Clear all learning paths from the in-memory store."""
    with _store_lock:
        _store.clear()
