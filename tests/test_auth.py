# tests/test_auth.py
# Tests for the authentication feature (register / login / logout / me).
#
# What is tested here
# --------------------
# 1. Register, login, logout, and /api/auth/me route behaviour via the
#    Flask test client.
# 2. Validation errors (short username/password, duplicate username,
#    wrong credentials).
# 3. Token round-trip — a token returned from register/login actually
#    authenticates against /api/auth/me.
# 4. Each test uses a unique username so tests don't collide with each
#    other against the shared SQLite-backed user store.
#
# Run with:  python -m pytest tests/test_auth.py -v

import sys
import os
import uuid

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


def _unique_username():
    """Generate a unique username so tests don't collide on the shared store."""
    return "test_" + uuid.uuid4().hex[:10]


# ---------------------------------------------------------------------------
# Register
# ---------------------------------------------------------------------------

def test_register_success(client):
    username = _unique_username()
    response = client.post("/api/auth/register", json={
        "username": username,
        "password": "testpass123"
    })
    assert response.status_code == 201
    data = response.get_json()
    assert "token" in data
    assert data["username"] == username
    assert "path_id" in data


def test_register_duplicate_username_rejected(client):
    username = _unique_username()
    client.post("/api/auth/register", json={
        "username": username,
        "password": "testpass123"
    })
    response = client.post("/api/auth/register", json={
        "username": username,
        "password": "anotherpass"
    })
    assert response.status_code == 400
    assert "error" in response.get_json()


def test_register_short_username_rejected(client):
    response = client.post("/api/auth/register", json={
        "username": "a",
        "password": "testpass123"
    })
    assert response.status_code == 400


def test_register_short_password_rejected(client):
    response = client.post("/api/auth/register", json={
        "username": _unique_username(),
        "password": "abc"
    })
    assert response.status_code == 400


def test_register_missing_body_rejected(client):
    response = client.post("/api/auth/register", json={})
    assert response.status_code == 400


def test_register_no_json_rejected(client):
    response = client.post("/api/auth/register")
    assert response.status_code == 400


def test_register_username_is_lowercased(client):
    username = _unique_username()
    response = client.post("/api/auth/register", json={
        "username": username.upper(),
        "password": "testpass123"
    })
    assert response.status_code == 201
    assert response.get_json()["username"] == username.upper().lower()


# ---------------------------------------------------------------------------
# Login
# ---------------------------------------------------------------------------

def test_login_success(client):
    username = _unique_username()
    client.post("/api/auth/register", json={
        "username": username,
        "password": "testpass123"
    })

    response = client.post("/api/auth/login", json={
        "username": username,
        "password": "testpass123"
    })
    assert response.status_code == 200
    data = response.get_json()
    assert "token" in data
    assert data["username"] == username


def test_login_wrong_password_rejected(client):
    username = _unique_username()
    client.post("/api/auth/register", json={
        "username": username,
        "password": "testpass123"
    })

    response = client.post("/api/auth/login", json={
        "username": username,
        "password": "wrongpass"
    })
    assert response.status_code == 401


def test_login_nonexistent_user_rejected(client):
    response = client.post("/api/auth/login", json={
        "username": _unique_username(),
        "password": "whatever123"
    })
    assert response.status_code == 401


def test_login_missing_body_rejected(client):
    response = client.post("/api/auth/login", json={})
    assert response.status_code == 400


# ---------------------------------------------------------------------------
# /api/auth/me
# ---------------------------------------------------------------------------

def test_me_with_valid_token(client):
    username = _unique_username()
    reg = client.post("/api/auth/register", json={
        "username": username,
        "password": "testpass123"
    })
    token = reg.get_json()["token"]

    response = client.get("/api/auth/me", headers={"X-Auth-Token": token})
    assert response.status_code == 200
    assert response.get_json()["username"] == username


def test_me_without_token_rejected(client):
    response = client.get("/api/auth/me")
    assert response.status_code == 401


def test_me_with_invalid_token_rejected(client):
    response = client.get(
        "/api/auth/me", headers={"X-Auth-Token": "not-a-real-token"}
    )
    assert response.status_code == 401


# ---------------------------------------------------------------------------
# Logout
# ---------------------------------------------------------------------------

def test_logout_invalidates_token(client):
    username = _unique_username()
    reg = client.post("/api/auth/register", json={
        "username": username,
        "password": "testpass123"
    })
    token = reg.get_json()["token"]

    logout_response = client.post(
        "/api/auth/logout", headers={"X-Auth-Token": token}
    )
    assert logout_response.status_code == 200

    me_response = client.get("/api/auth/me", headers={"X-Auth-Token": token})
    assert me_response.status_code == 401


def test_logout_without_token_does_not_crash(client):
    response = client.post("/api/auth/logout")
    assert response.status_code == 200


# ---------------------------------------------------------------------------
# End-to-end: register then immediately use the path_id with the
# existing learning-path API (this is the integration point auth.js relies on)
# ---------------------------------------------------------------------------

def test_register_then_create_learning_path(client):
    username = _unique_username()
    reg = client.post("/api/auth/register", json={
        "username": username,
        "password": "testpass123"
    })
    reg_data = reg.get_json()
    token = reg_data["token"]
    path_id = reg_data["path_id"]

    response = client.post(
        f"/api/learning-path/{path_id}",
        json={"points": 10, "searches": 1},
        headers={"X-Learning-Path-Token": token}
    )
    # Accept 200/201 depending on whether the endpoint treats this as
    # a create or an update.
    assert response.status_code in (200, 201)
