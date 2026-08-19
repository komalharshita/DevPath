# tests/test_profile_sections.py
# Tests for issue #1826: the /profile "Saved Skills" and "Bookmarked Projects"
# sections could never populate (their DB columns were never written), so they
# and their misleading empty-state copy are removed.

import pytest


@pytest.fixture
def client():
    from app import app
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def _login(client):
    from models import db, User
    user = User(github_id="test-1826", username="tester")
    db.session.add(user)
    db.session.commit()
    with client.session_transaction() as sess:
        sess["user_id"] = user.id
    return user


def test_profile_renders_for_logged_in_user(client):
    """The profile page must still render for an authenticated user."""
    _login(client)
    response = client.get("/profile")
    assert response.status_code == 200
    assert b"tester" in response.data


def test_profile_redirects_when_logged_out(client):
    """Unauthenticated users must be redirected to the login page."""
    response = client.get("/profile")
    assert response.status_code == 302


def test_profile_has_no_saved_skills_section(client):
    """The dead 'Saved Skills' section and its copy must be gone."""
    _login(client)
    response = client.get("/profile")
    assert b"Saved Skills" not in response.data
    assert b"Your search history will automatically populate" not in response.data


def test_profile_has_no_bookmarked_projects_section(client):
    """The dead 'Bookmarked Projects' section must be gone."""
    _login(client)
    response = client.get("/profile")
    assert b"Bookmarked Projects" not in response.data


def test_profile_keeps_account_management(client):
    """The Account Management section must remain."""
    _login(client)
    response = client.get("/profile")
    assert b"Account Management" in response.data
