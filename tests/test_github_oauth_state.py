# tests/test_github_oauth_state.py
# Tests for issue #1828: GitHub OAuth login must generate and persist a
# `state` parameter and the callback must reject missing/mismatched states.

import pytest


@pytest.fixture
def client(monkeypatch):
    from routes import github_routes
    monkeypatch.setattr(github_routes, "GITHUB_CLIENT_ID", "test-client-id")
    monkeypatch.setattr(github_routes, "GITHUB_CLIENT_SECRET", "test-client-secret")
    from app import app
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def test_login_redirects_with_state(client):
    response = client.get("/api/github/login")
    assert response.status_code == 302
    location = response.headers["Location"]
    assert "state=" in location


def test_login_persists_state_in_session(client):
    client.get("/api/github/login")
    with client.session_transaction() as sess:
        state = sess.get("github_oauth_state")
    assert state


def test_callback_rejects_missing_state(client):
    response = client.get("/api/github/callback?code=abc123")
    assert response.status_code == 302
    assert "/?github_auth=error" in response.headers["Location"]


def test_callback_rejects_wrong_state(client):
    client.get("/api/github/login")
    response = client.get("/api/github/callback?code=abc123&state=not-the-right-state")
    assert response.status_code == 302
    assert "/?github_auth=error" in response.headers["Location"]
