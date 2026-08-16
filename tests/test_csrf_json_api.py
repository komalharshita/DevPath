# tests/test_csrf_json_api.py
# Integration tests proving the JSON-only API endpoints work when CSRF
# protection is ENABLED (as it is in production), while form-based endpoints
# still require a CSRF token.
#
# conftest.py disables CSRF globally for the test suite; this file re-enables
# it so the production code path is actually exercised.

import pytest

from app import app


@pytest.fixture
def csrf_client():
    """Test client with Flask-WTF CSRF protection fully enabled."""
    app.config["WTF_CSRF_ENABLED"] = True
    app.config["TESTING"] = True
    try:
        with app.test_client() as client:
            yield client
    finally:
        app.config["WTF_CSRF_ENABLED"] = False


def test_recommend_json_post_works_with_csrf_enabled(csrf_client):
    """/api/recommend must return its normal JSON response (not 400 CSRF)."""
    resp = csrf_client.post(
        "/api/recommend",
        json={
            "skills": "Python",
            "level": "Beginner",
            "interest": ["Data"],
            "time": "Low",
        },
    )
    assert resp.status_code == 200
    assert "projects" in resp.get_json()


def test_user_progress_json_post_passes_csrf(csrf_client):
    """/api/user-progress must not be rejected with a CSRF error."""
    resp = csrf_client.post("/api/user-progress", json={"data": {"points": 1}})
    # Unauthenticated -> 401 Unauthorized, NOT 400 CSRF token missing.
    assert resp.status_code == 401
    assert b"CSRF" not in resp.data


def test_project_progress_json_post_passes_csrf(csrf_client):
    """/api/project/<id>/progress must not be rejected with a CSRF error."""
    resp = csrf_client.post(
        "/api/project/1/progress", json={"completed_steps": [True, False]}
    )
    assert resp.status_code == 401
    assert b"CSRF" not in resp.data


def test_portfolio_analysis_json_post_works_with_csrf_enabled(csrf_client):
    """/api/portfolio-analysis must return its normal JSON response."""
    resp = csrf_client.post(
        "/api/portfolio-analysis", json={"completed_projects": [1]}
    )
    assert resp.status_code == 200
    assert "score" in resp.get_json()


def test_form_post_still_requires_csrf_token(csrf_client):
    """Form-based POSTs must still be rejected without a CSRF token."""
    resp = csrf_client.post("/project/1/export_github")
    assert resp.status_code == 400
