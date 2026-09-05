# tests/test_admin_csrf.py
# Tests for issue #1829: admin forms must include a CSRF token so the
# admin CRUD actions are not rejected by CSRFProtect.

import pytest


@pytest.fixture
def client():
    from app import app
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def _login_admin(client):
    from models import db, User
    admin = User(github_id="admin-1829", username="admin", is_admin=True)
    db.session.add(admin)
    db.session.commit()
    with client.session_transaction() as sess:
        sess["user_id"] = admin.id


def test_admin_new_project_form_has_csrf_token(client):
    """The create/edit form must render a csrf_token hidden input."""
    _login_admin(client)
    response = client.get("/admin/projects/new")
    assert response.status_code == 200
    assert b'name="csrf_token"' in response.data


def test_admin_dashboard_delete_form_has_csrf_token(client):
    """The delete form must render a csrf_token hidden input."""
    _login_admin(client)
    response = client.get("/admin/")
    assert response.status_code == 200
    assert b'name="csrf_token"' in response.data


def test_admin_create_rejected_without_csrf_when_enabled(client):
    """With CSRF enabled, a POST without a token must be rejected."""
    from app import app
    app.config["WTF_CSRF_ENABLED"] = True
    try:
        _login_admin(client)
        response = client.post("/admin/projects/new", data={
            "title": "Test Project",
            "level": "Beginner",
            "interest": "Web",
            "time": "Low",
            "description": "desc",
        })
        assert response.status_code == 400
    finally:
        app.config["WTF_CSRF_ENABLED"] = False


def test_admin_create_succeeds_with_csrf_when_enabled(client):
    """With CSRF enabled, a POST including the form's token must succeed."""
    import re
    from app import app
    app.config["WTF_CSRF_ENABLED"] = True
    try:
        _login_admin(client)

        # Fetch the create form to obtain a valid CSRF token from the session.
        form = client.get("/admin/projects/new")
        match = re.search(rb'name="csrf_token" value="([^"]+)"', form.data)
        assert match is not None
        token = match.group(1).decode()

        response = client.post("/admin/projects/new", data={
            "title": "Test Project",
            "level": "Beginner",
            "interest": "Web",
            "time": "Low",
            "description": "desc",
            "csrf_token": token,
        })
        assert response.status_code == 302
    finally:
        app.config["WTF_CSRF_ENABLED"] = False
