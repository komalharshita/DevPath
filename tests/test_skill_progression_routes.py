"""
Route-level tests for the skill progression API.

Run with:   python -m pytest tests/test_skill_progression_routes.py
Or:         python tests/test_skill_progression_routes.py

These tests exercise /api/skill-progression/record end-to-end, verifying
that prerequisites are enforced and that difficulty never regresses.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from app import app


def get_client():
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False
    return app.test_client()


def test_record_rejects_unmet_prerequisites():
    """Claiming a level without its baseline prerequisites returns 400."""
    client = get_client()
    response = client.post("/api/skill-progression/record", json={
        "user_id": "user-1869-prereq",
        "skill": "React",
        "difficulty": "ADVANCED",
    })
    assert response.status_code == 400
    data = response.get_json()
    assert data["error"]


def test_record_preserves_higher_difficulty_on_downgrade():
    """Re-recording at a lower difficulty must not wipe earned progress."""
    client = get_client()
    user_id = "user-1869-downgrade"

    for level in ("BEGINNER", "INTERMEDIATE", "ADVANCED", "EXPERT"):
        response = client.post("/api/skill-progression/record", json={
            "user_id": user_id,
            "skill": "Python",
            "difficulty": level,
            "assessment_score": 90,
        })
        assert response.status_code == 201

    downgrade = client.post("/api/skill-progression/record", json={
        "user_id": user_id,
        "skill": "Python",
        "difficulty": "BEGINNER",
        "assessment_score": 60,
    })
    assert downgrade.status_code == 201
    assert downgrade.get_json()["skill_data"]["difficulty"] == "EXPERT"


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v", "--no-header"]))
