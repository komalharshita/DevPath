# tests/test_leaderboard.py
# Tests for issue #1834: the leaderboard is ranked from real UserGameProgress
# data instead of hardcoded placeholder entries.

import pytest


@pytest.fixture
def client():
    from app import app
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def _add_user(username, github_id, points):
    from models import db, User, UserGameProgress
    user = User(github_id=github_id, username=username)
    db.session.add(user)
    db.session.flush()
    progress = UserGameProgress(user_id=user.id, data={"points": points})
    db.session.add(progress)
    db.session.commit()
    return user


def test_leaderboard_requires_auth(client):
    resp = client.get("/api/leaderboard")
    assert resp.status_code == 401


def test_leaderboard_returns_top_users_by_points(client):
    _add_user("Alice", "gh-alice", 300)
    _add_user("Bob", "gh-bob", 150)
    _add_user("Carol", "gh-carol", 450)

    with client.session_transaction() as sess:
        sess["user_id"] = 1

    resp = client.get("/api/leaderboard")
    assert resp.status_code == 200
    entries = resp.get_json()["leaderboard"]
    assert [entry["name"] for entry in entries] == ["Carol", "Alice", "Bob"]
    assert entries[0]["points"] == 450


def test_leaderboard_limits_to_top_ten(client):
    for i in range(12):
        _add_user(f"User{i}", f"gh-user{i}", i * 10)

    with client.session_transaction() as sess:
        sess["user_id"] = 1

    resp = client.get("/api/leaderboard")
    entries = resp.get_json()["leaderboard"]
    assert len(entries) == 10
    assert entries[0]["name"] == "User11"


def test_leaderboard_handles_missing_points(client):
    from models import db, User, UserGameProgress
    user = User(github_id="gh-novalue", username="NoValue")
    db.session.add(user)
    db.session.flush()
    progress = UserGameProgress(user_id=user.id, data={})
    db.session.add(progress)
    db.session.commit()

    with client.session_transaction() as sess:
        sess["user_id"] = user.id

    resp = client.get("/api/leaderboard")
    assert resp.status_code == 200
    assert resp.get_json()["leaderboard"] == [{"name": "NoValue", "points": 0}]
