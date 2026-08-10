# tests/test_github_oauth.py
# Tests for the consolidated GitHub OAuth flow (issue #1814).
#
# Previously there were two incompatible OAuth implementations:
#   - Authlib flow (/auth/login, /auth/authorize) stores a token *dict* in
#     session['github_token'] and creates a User + sets session['user_id'].
#   - Manual flow (/api/github/login, /api/github/callback) stored a bare
#     token *string* and never created a User.
#
# The manual routes now alias the Authlib flow, and export_github handles
# both token shapes defensively so legacy sessions cannot crash it.

import sys
import os

from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from app import app


def get_client():
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False
    return app.test_client()


# ============================================================
# Consolidated OAuth entry points
# ============================================================

def test_api_github_login_redirects_to_authlib_flow():
    """/api/github/login must forward into the canonical Authlib flow."""
    client = get_client()
    response = client.get("/api/github/login")
    assert response.status_code == 302
    assert "/auth/login" in response.headers["Location"]


def test_api_github_callback_redirects_to_authlib_flow():
    """Legacy /api/github/callback must not 404 and must forward to Authlib."""
    client = get_client()
    response = client.get("/api/github/callback?code=legacy-code")
    assert response.status_code == 302
    assert "/auth/login" in response.headers["Location"]


def test_auth_login_still_redirects_to_github_authorize():
    """The canonical /auth/login must still start a GitHub OAuth round trip."""
    client = get_client()
    response = client.get("/auth/login")
    assert response.status_code == 302
    assert "github.com/login/oauth/authorize" in response.headers["Location"]


# ============================================================
# /api/github/repos
# ============================================================

def test_github_repos_requires_auth():
    client = get_client()
    response = client.get("/api/github/repos")
    assert response.status_code == 401


@patch("routes.github_routes.requests.get")
def test_github_repos_with_dict_token(mock_get):
    """Repos endpoint must work with the Authlib dict token shape."""
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = [{"name": "devpath"}]
    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess["github_token"] = {"access_token": "abc", "token_type": "bearer"}
        response = client.get("/api/github/repos")
    assert response.status_code == 200
    assert response.get_json() == [{"name": "devpath"}]


# ============================================================
# export_github with both token shapes
# ============================================================

def _seed_project_with_starter_code():
    """Ensure a project with a starter_code file exists for export tests."""
    with app.app_context():
        from models import db, Project
        p = db.session.get(Project, 1000)
        if not p:
            p = Project(
                id=1000,
                title="Valid Code",
                level="Beg",
                interest="Web",
                time="Low",
                description="Desc",
                starter_code="expense_tracker.py",
            )
            db.session.add(p)
            db.session.commit()


@patch("routes.main_routes.requests.put")
@patch("routes.main_routes.requests.post")
@patch("routes.main_routes.requests.get")
def test_export_github_with_dict_token_succeeds(mock_get, mock_post, mock_put):
    """The Authlib dict token shape must flow through export_github."""
    _seed_project_with_starter_code()
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {"login": "testuser"}
    mock_post.return_value.status_code = 201
    mock_put.return_value.status_code = 201

    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess["github_token"] = {
                "access_token": "abc",
                "token_type": "bearer",
                "expires_in": 3600,
            }
        response = client.post("/project/1000/export_github")

    assert response.status_code == 302
    assert "github.com/testuser/DevPath-Starter-valid-code" in response.headers["Location"]


@patch("routes.main_routes.requests.put")
@patch("routes.main_routes.requests.post")
@patch("routes.main_routes.requests.get")
def test_export_github_with_legacy_string_token_does_not_crash(mock_get, mock_post, mock_put):
    """A legacy bare-string token must NOT raise TypeError (issue #1814)."""
    _seed_project_with_starter_code()
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {"login": "testuser"}
    mock_post.return_value.status_code = 201
    mock_put.return_value.status_code = 201

    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess["github_token"] = "legacy-string-token"
        response = client.post("/project/1000/export_github")

    assert response.status_code == 302
    assert "github.com/testuser/DevPath-Starter-valid-code" in response.headers["Location"]
