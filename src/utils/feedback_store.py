import json
import os
import threading
from datetime import datetime

DATA_FILE = os.path.join(
    os.path.dirname(__file__),
    "..",
    "..",
    "data",
    "feedback.json",
)

_lock = threading.Lock()


def _ensure_file():
    """Create feedback file if it does not exist."""
    if not os.path.exists(DATA_FILE):
        os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)

        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump([], f)


def save_feedback(project_id, feedback_type):
    """
    Persist recommendation feedback.

    feedback_type:
        "like"
        "dislike"
    """
    _ensure_file()

    entry = {
    "project_id": project_id,
    "feedback": feedback_type,
    "timestamp": datetime.utcnow().isoformat() + "Z",

    # Future ranking features
    "weight": 1,
    "source": "user_feedback"
}

    with _lock:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        data.append(entry)

        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    return entry