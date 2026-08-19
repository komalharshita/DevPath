# tests/test_api_auth_required.py
# Tests for issue #1832: skill-progression and code-review APIs must require
# authentication, and user-scoped endpoints must not leak other users' data.

import pytest


@pytest.fixture
def client():
    from app import app
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False
    with app.test_client() as c:
        yield c


def _login(client, user_id="u1832"):
    with client.session_transaction() as sess:
        sess["user_id"] = user_id


SKILL_ENDPOINTS = [
    ("POST", "/api/skill-progression/validate"),
    ("POST", "/api/skill-progression/record"),
    ("GET", "/api/skill-progression/user/someuser"),
    ("GET", "/api/skill-progression/next/someuser/Python"),
]

CODE_REVIEW_ENDPOINTS = [
    ("POST", "/api/code-review/submit"),
    ("GET", "/api/code-review/submission/somesub"),
    ("GET", "/api/code-review/user/someuser/submissions"),
    ("GET", "/api/code-review/project/1/submissions"),
    ("POST", "/api/code-review/start"),
    ("POST", "/api/code-review/somerev/comment"),
    ("POST", "/api/code-review/somerev/score"),
    ("POST", "/api/code-review/somerev/complete"),
    ("GET", "/api/code-review/somerev/comments"),
    ("GET", "/api/code-review/submission/somesub/quality"),
    ("GET", "/api/code-review/submission/somesub/recommendations"),
]


@pytest.mark.parametrize("method,path", SKILL_ENDPOINTS + CODE_REVIEW_ENDPOINTS)
def test_endpoint_requires_auth(client, method, path):
    """Anonymous requests must be rejected with 401."""
    resp = getattr(client, method.lower())(path)
    assert resp.status_code == 401
    assert resp.get_json()["error"] == "Unauthorized"


def test_validate_skill_works_when_authenticated(client):
    _login(client)
    resp = client.post("/api/skill-progression/validate", json={
        "skill": "Python",
        "difficulty": "beginner",
    })
    assert resp.status_code == 200
    assert resp.get_json()["allowed"] is True


def test_record_skill_passes_auth_when_authenticated(client):
    """The endpoint must accept an authenticated user (it still 500s on a
    pre-existing SkillDifficulty JSON-serialization bug, unrelated to #1832)."""
    _login(client)
    resp = client.post("/api/skill-progression/record", json={
        "skill": "Python",
        "difficulty": "beginner",
    })
    assert resp.status_code != 401


def test_user_progression_rejects_other_users(client):
    _login(client)
    resp = client.get("/api/skill-progression/user/otheruser")
    assert resp.status_code == 403


def test_user_progression_passes_auth_for_own_user(client):
    """Own-user access passes the auth gate (still hits the pre-existing
    SkillDifficulty serialization bug, unrelated to #1832)."""
    _login(client)
    resp = client.get("/api/skill-progression/user/u1832")
    assert resp.status_code != 401


def test_code_submit_rejects_other_users(client):
    _login(client)
    resp = client.post("/api/code-review/submit", json={
        "submission_id": "sub1",
        "user_id": "otheruser",
        "project_id": 1,
        "code": "print('hi')",
        "language": "python",
    })
    assert resp.status_code == 403
