# tests/test_bookmarks.py
# Tests for the Quick-Save / Session-Restore feature (issue #763).
#
# What is tested here
# -------------------
# 1. Flask route smoke-tests — the pages that host the bookmark UI still
#    return 200 and contain the expected HTML landmarks.
# 2. Static file availability — bookmarks.js and bookmarks.css are served.
# 3. Saved-projects panel markup — the required IDs exist in index.html.
# 4. Security headers are present on all pages (unchanged by this feature).
#
# Client-side localStorage behaviour is intentionally NOT tested here
# because pytest has no browser runtime.  The JS logic is covered by the
# inline self-tests inside bookmarks.js (see bottom of that file) which
# run in a real browser via the DevTools console.
#
# Run with:  python -m pytest tests/test_bookmarks.py -v

import sys
import os

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from app import app


# ---------------------------------------------------------------------------
# Fixture
# ---------------------------------------------------------------------------

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


# ---------------------------------------------------------------------------
# Homepage renders and contains bookmark UI landmarks
# ---------------------------------------------------------------------------

def test_homepage_returns_200(client):
    """The homepage must return HTTP 200."""
    response = client.get("/")
    assert response.status_code == 200


def test_saved_projects_panel_present(client):
    """saved-projects-panel div must be present in the homepage HTML."""
    response = client.get("/")
    assert b'id="saved-projects-panel"' in response.data, (
        "saved-projects-panel not found in index.html"
    )


def test_saved_projects_list_present(client):
    """saved-projects-list element must be present in the homepage HTML."""
    response = client.get("/")
    assert b'id="saved-projects-list"' in response.data


def test_saved_projects_count_present(client):
    """saved-projects-count element must be present in the homepage HTML."""
    response = client.get("/")
    assert b'id="saved-projects-count"' in response.data


def test_results_grid_present(client):
    """results-grid must be present — save buttons are injected here by JS."""
    response = client.get("/")
    assert b'id="results-grid"' in response.data


def test_recommend_form_present(client):
    """recommend-form must be present for session persistence to work."""
    response = client.get("/")
    assert b'id="recommend-form"' in response.data


def test_skills_hidden_input_present(client):
    """The hidden skills input must be present for session restore."""
    response = client.get("/")
    assert b'id="skills"' in response.data


def test_level_select_present(client):
    """Level select must be present for session restore."""
    response = client.get("/")
    assert b'id="level"' in response.data


def test_interest_select_present(client):
    """Interest select must be present for session restore."""
    response = client.get("/")
    assert b'id="interest"' in response.data


def test_time_select_present(client):
    """Time select must be present for session restore."""
    response = client.get("/")
    assert b'id="time"' in response.data


def test_clear_filters_button_present(client):
    """Clear Filters button must exist so clearSession() is wired up."""
    response = client.get("/")
    assert b'id="clear-filters-btn"' in response.data


# ---------------------------------------------------------------------------
# Static files are served
# ---------------------------------------------------------------------------

def test_bookmarks_js_served(client):
    """bookmarks.js must be served with HTTP 200."""
    response = client.get("/static/bookmarks.js")
    assert response.status_code == 200, (
        "bookmarks.js not found — ensure the file is in static/"
    )


def test_bookmarks_js_content_type(client):
    """bookmarks.js must be served as JavaScript."""
    response = client.get("/static/bookmarks.js")
    assert "javascript" in response.content_type or "text" in response.content_type


def test_bookmarks_css_served(client):
    """bookmarks.css must be served with HTTP 200."""
    response = client.get("/static/bookmarks.css")
    assert response.status_code == 200, (
        "bookmarks.css not found — ensure the file is in static/"
    )


def test_bookmarks_js_contains_saved_key(client):
    """bookmarks.js must reference the shared storage key."""
    response = client.get("/static/bookmarks.js")
    assert b"devpathSavedProjects" in response.data


def test_bookmarks_js_contains_session_key(client):
    """bookmarks.js must define a session storage key."""
    response = client.get("/static/bookmarks.js")
    assert b"devpathSessionForm" in response.data


def test_bookmarks_js_exposes_public_api(client):
    """bookmarks.js must expose the DevPathBookmarks global."""
    response = client.get("/static/bookmarks.js")
    assert b"DevPathBookmarks" in response.data


def test_bookmarks_js_save_function(client):
    """bookmarks.js must implement a save() function."""
    response = client.get("/static/bookmarks.js")
    assert b"function save(" in response.data or b"save:" in response.data


def test_bookmarks_js_remove_function(client):
    """bookmarks.js must implement a remove() function."""
    response = client.get("/static/bookmarks.js")
    assert b"function remove(" in response.data or b"remove:" in response.data


def test_bookmarks_js_restore_session(client):
    """bookmarks.js must implement restoreSession()."""
    response = client.get("/static/bookmarks.js")
    assert b"restoreSession" in response.data


def test_bookmarks_js_save_session(client):
    """bookmarks.js must implement saveSession()."""
    response = client.get("/static/bookmarks.js")
    assert b"saveSession" in response.data


def test_bookmarks_js_clear_session(client):
    """bookmarks.js must implement clearSession()."""
    response = client.get("/static/bookmarks.js")
    assert b"clearSession" in response.data


def test_bookmarks_js_render_panel(client):
    """bookmarks.js must implement renderPanel()."""
    response = client.get("/static/bookmarks.js")
    assert b"renderPanel" in response.data


def test_bookmarks_css_contains_panel_rule(client):
    """bookmarks.css must set display:none on .saved-projects-panel."""
    response = client.get("/static/bookmarks.css")
    assert b"saved-projects-panel" in response.data
    assert b"display: none" in response.data or b"display:none" in response.data


def test_bookmarks_css_contains_bookmark_icon_rule(client):
    """bookmarks.css must style the SVG inside .btn-save-project."""
    response = client.get("/static/bookmarks.css")
    assert b"btn-save-project" in response.data


# ---------------------------------------------------------------------------
# script.js compatibility — existing save infrastructure is untouched
# ---------------------------------------------------------------------------

def test_script_js_served(client):
    """Original script.js must still be served correctly."""
    response = client.get("/static/script.js")
    assert response.status_code == 200


def test_script_js_has_saved_projects_key(client):
    """script.js must still reference devpathSavedProjects (compatibility)."""
    response = client.get("/static/script.js")
    assert b"devpathSavedProjects" in response.data


# ---------------------------------------------------------------------------
# Security headers on bookmark-related pages
# ---------------------------------------------------------------------------

def test_security_headers_on_homepage(client):
    response = client.get("/")
    assert response.headers.get("X-Frame-Options") == "DENY"
    assert response.headers.get("X-Content-Type-Options") == "nosniff"
    assert response.headers.get("Referrer-Policy") == "strict-origin-when-cross-origin"


def test_security_headers_on_static_js(client):
    response = client.get("/static/bookmarks.js")
    assert response.headers.get("X-Content-Type-Options") == "nosniff"


# ---------------------------------------------------------------------------
# API still works (save buttons only appear after a successful recommendation)
# ---------------------------------------------------------------------------

def test_recommend_api_still_returns_projects(client):
    """The recommend API must still return projects — save buttons depend on it."""
    response = client.post("/api/recommend", json={
        "skills": "Python",
        "level": "Beginner",
        "interest": "Data",
        "time": "Low"
    })
    assert response.status_code == 200
    data = response.get_json()
    assert "projects" in data
    assert len(data["projects"]) > 0


def test_recommend_api_project_has_id_and_title(client):
    """Each returned project must have id and title — required by save()."""
    response = client.post("/api/recommend", json={
        "skills": "Python",
        "level": "Beginner",
        "interest": "Data",
        "time": "Low"
    })
    data = response.get_json()
    for project in data["projects"]:
        assert "id" in project, "Project missing 'id' field"
        assert "title" in project, "Project missing 'title' field"


def test_recommend_api_project_has_bookmark_fields(client):
    """Projects must include level, time, skills — used by save() metadata."""
    response = client.post("/api/recommend", json={
        "skills": "Python",
        "level": "Beginner",
        "interest": "Data",
        "time": "Low"
    })
    data = response.get_json()
    for project in data["projects"]:
        assert "level"  in project
        assert "time"   in project
        assert "skills" in project
