# tests/test_learning_path.py
# Tests for the learning path API and its ownership-verification layer.
#
# Run with:   python -m pytest tests/test_learning_path.py
# Or:         python tests/test_learning_path.py
#
# Test categories:
#   1. Unit tests for utils/learning_path.py (storage + auth logic)
#   2. HTTP route tests via the Flask test client
#
# Each test that writes to the store calls _clear_all() in a setup step so
# tests are fully independent of each other and of test ordering.

import sys
import os
import secrets

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from utils.learning_path import (
    create_learning_path,
    get_learning_path,
    update_learning_path,
    path_exists,
    _clear_all,
    PathNotFoundError,
    PathAlreadyExistsError,
    AuthorizationError,
)
from app import app

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

TOKEN_HEADER = "X-Learning-Path-Token"


def make_token():
    """Return a fresh random token suitable for testing."""
    return secrets.token_urlsafe(32)


def get_client():
    """Return a Flask test client with testing mode enabled."""
    app.config["TESTING"] = True
    return app.test_client()


# ---------------------------------------------------------------------------
# 1. Unit tests — utils/learning_path.py
# ---------------------------------------------------------------------------

class TestCreateLearningPath:

    def setup_method(self):
        _clear_all()

    def test_create_stores_data(self):
        """Creating a path should make it retrievable with the correct token."""
        token = make_token()
        create_learning_path("path-1", token, {"step": 1})
        data = get_learning_path("path-1", token)
        assert data == {"step": 1}

    def test_create_path_exists_returns_true(self):
        """path_exists should return True after creation."""
        token = make_token()
        create_learning_path("path-2", token, {})
        assert path_exists("path-2") is True

    def test_create_duplicate_raises(self):
        """Creating the same path_id twice should raise PathAlreadyExistsError."""
        token = make_token()
        create_learning_path("dup", token, {})
        with pytest.raises(PathAlreadyExistsError):
            create_learning_path("dup", token, {"step": 2})

    def test_create_returns_copy_of_data(self):
        """Mutating the dict passed to create should not affect the stored value."""
        data = {"step": 1}
        token = make_token()
        create_learning_path("copy-test", token, data)
        data["step"] = 999
        retrieved = get_learning_path("copy-test", token)
        assert retrieved["step"] == 1

    def test_create_invalid_path_id_raises(self):
        """path_id with illegal characters should raise ValueError."""
        with pytest.raises(ValueError):
            create_learning_path("bad path!", make_token(), {})

    def test_create_path_id_with_exclamation_raises(self):
        """path_id containing '!' must be rejected by validation."""
        with pytest.raises(ValueError):
            create_learning_path("bad!path", make_token(), {})

    def test_create_empty_path_id_raises(self):
        """Empty path_id should raise ValueError."""
        with pytest.raises(ValueError):
            create_learning_path("", make_token(), {})

    def test_create_empty_token_raises(self):
        """Empty token should raise ValueError."""
        with pytest.raises(ValueError):
            create_learning_path("p1", "", {})

    def test_create_non_dict_data_raises(self):
        """Passing a list as data should raise ValueError."""
        with pytest.raises(ValueError):
            create_learning_path("p1", make_token(), ["not", "a", "dict"])


class TestGetLearningPath:

    def setup_method(self):
        _clear_all()

    def test_get_correct_token_returns_data(self):
        """GET with the correct token should return the stored data."""
        token = make_token()
        create_learning_path("get-1", token, {"progress": 42})
        assert get_learning_path("get-1", token) == {"progress": 42}

    def test_get_wrong_token_raises_authorization_error(self):
        """GET with the wrong token should raise AuthorizationError."""
        token = make_token()
        create_learning_path("get-2", token, {})
        with pytest.raises(AuthorizationError):
            get_learning_path("get-2", make_token())

    def test_get_missing_path_raises_not_found(self):
        """GET for a non-existent path_id should raise PathNotFoundError."""
        with pytest.raises(PathNotFoundError):
            get_learning_path("does-not-exist", make_token())

    def test_get_returns_copy_not_reference(self):
        """Mutating the dict returned by get should not affect the store."""
        token = make_token()
        create_learning_path("ref-test", token, {"x": 1})
        result = get_learning_path("ref-test", token)
        result["x"] = 999
        assert get_learning_path("ref-test", token)["x"] == 1


class TestUpdateLearningPath:

    def setup_method(self):
        _clear_all()

    def test_update_replaces_data(self):
        """PUT with the correct token should overwrite the stored data."""
        token = make_token()
        create_learning_path("upd-1", token, {"step": 1})
        update_learning_path("upd-1", token, {"step": 2, "done": True})
        assert get_learning_path("upd-1", token) == {"step": 2, "done": True}

    def test_update_wrong_token_raises_authorization_error(self):
        """PUT with the wrong token should raise AuthorizationError."""
        token = make_token()
        create_learning_path("upd-2", token, {})
        with pytest.raises(AuthorizationError):
            update_learning_path("upd-2", make_token(), {"x": 1})

    def test_update_missing_path_raises_not_found(self):
        """PUT for a non-existent path_id should raise PathNotFoundError."""
        with pytest.raises(PathNotFoundError):
            update_learning_path("ghost", make_token(), {})

    def test_update_does_not_change_token(self):
        """After a successful PUT the original token must still work."""
        token = make_token()
        create_learning_path("token-stable", token, {"v": 1})
        update_learning_path("token-stable", token, {"v": 2})
        # Original token still grants access
        assert get_learning_path("token-stable", token)["v"] == 2


class TestPathExists:

    def setup_method(self):
        _clear_all()

    def test_nonexistent_path_returns_false(self):
        assert path_exists("no-such-path") is False

    def test_existing_path_returns_true(self):
        token = make_token()
        create_learning_path("exists-1", token, {})
        assert path_exists("exists-1") is True

    def test_non_string_path_id_returns_false(self):
        assert path_exists(None) is False
        assert path_exists(123) is False


class TestTokenComparison:

    def setup_method(self):
        _clear_all()

    def test_similar_tokens_are_rejected(self):
        """A token differing by a single character must not be accepted."""
        token = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
        wrong = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaab"
        create_learning_path("near-miss", token, {"secret": True})
        with pytest.raises(AuthorizationError):
            get_learning_path("near-miss", wrong)

    def test_empty_token_on_get_raises_value_error(self):
        token = make_token()
        create_learning_path("empty-tok", token, {})
        with pytest.raises(ValueError):
            get_learning_path("empty-tok", "")

    def test_whitespace_only_token_raises_value_error(self):
        token = make_token()
        create_learning_path("ws-tok", token, {})
        with pytest.raises(ValueError):
            get_learning_path("ws-tok", "   ")


# ---------------------------------------------------------------------------
# 2. HTTP route tests — /api/learning-path/<path_id>
# ---------------------------------------------------------------------------

class TestCreatePathRoute:

    def setup_method(self):
        _clear_all()

    def test_post_creates_path_returns_201(self):
        client = get_client()
        token = make_token()
        response = client.post(
            "/api/learning-path/my-path-1",
            json={"step": 1},
            headers={TOKEN_HEADER: token},
        )
        assert response.status_code == 201
        data = response.get_json()
        assert data["path_id"] == "my-path-1"
        assert "message" in data

    def test_post_missing_token_header_returns_400(self):
        client = get_client()
        response = client.post("/api/learning-path/my-path-2", json={"step": 1})
        assert response.status_code == 400
        assert "error" in response.get_json()

    def test_post_non_json_body_returns_400(self):
        client = get_client()
        response = client.post(
            "/api/learning-path/my-path-3",
            data="not json",
            content_type="text/plain",
            headers={TOKEN_HEADER: make_token()},
        )
        assert response.status_code == 400

    def test_post_body_is_array_returns_400(self):
        client = get_client()
        response = client.post(
            "/api/learning-path/my-path-4",
            json=[1, 2, 3],
            headers={TOKEN_HEADER: make_token()},
        )
        assert response.status_code == 400

    def test_post_duplicate_path_id_returns_409(self):
        client = get_client()
        token = make_token()
        client.post(
            "/api/learning-path/dup-path",
            json={},
            headers={TOKEN_HEADER: token},
        )
        response = client.post(
            "/api/learning-path/dup-path",
            json={"x": 1},
            headers={TOKEN_HEADER: token},
        )
        assert response.status_code == 409

    def test_post_invalid_path_id_characters_returns_400(self):
        """path_id containing '!' (an illegal special character) must be rejected with 400.

        The validation regex only permits letters, digits, hyphens, and
        underscores.  An exclamation mark is explicitly illegal and is
        consistent with the unit-level test ``test_create_invalid_path_id_raises``
        which also uses '!'.  The character is URL-encoded (%21) so that Flask
        routes the request to the handler rather than returning a 404 for an
        unroutable path.
        """
        client = get_client()
        response = client.post(
            "/api/learning-path/bad%21path",
            json={},
            headers={TOKEN_HEADER: make_token()},
        )
        assert response.status_code == 400


class TestReadPathRoute:

    def setup_method(self):
        _clear_all()

    def _seed(self, path_id, token, data):
        client = get_client()
        client.post(
            f"/api/learning-path/{path_id}",
            json=data,
            headers={TOKEN_HEADER: token},
        )

    def test_get_correct_token_returns_200_with_data(self):
        token = make_token()
        self._seed("read-1", token, {"progress": 5})
        client = get_client()
        response = client.get(
            "/api/learning-path/read-1",
            headers={TOKEN_HEADER: token},
        )
        assert response.status_code == 200
        body = response.get_json()
        assert body["path_id"] == "read-1"
        assert body["data"] == {"progress": 5}

    def test_get_wrong_token_returns_403(self):
        """A request with a wrong token must be rejected with 403 Forbidden."""
        token = make_token()
        self._seed("read-2", token, {"secret": True})
        client = get_client()
        response = client.get(
            "/api/learning-path/read-2",
            headers={TOKEN_HEADER: make_token()},  # different token
        )
        assert response.status_code == 403
        assert "error" in response.get_json()

    def test_get_missing_token_returns_400(self):
        token = make_token()
        self._seed("read-3", token, {})
        client = get_client()
        response = client.get("/api/learning-path/read-3")
        assert response.status_code == 400

    def test_get_nonexistent_path_returns_404(self):
        client = get_client()
        response = client.get(
            "/api/learning-path/ghost-path",
            headers={TOKEN_HEADER: make_token()},
        )
        assert response.status_code == 404

    def test_get_does_not_expose_other_users_data(self):
        """User B must not be able to read User A's learning path."""
        token_a = make_token()
        token_b = make_token()
        self._seed("shared-id", token_a, {"private": "user_a_data"})
        client = get_client()
        response = client.get(
            "/api/learning-path/shared-id",
            headers={TOKEN_HEADER: token_b},
        )
        assert response.status_code == 403
        # Confirm the private value is not present anywhere in the response
        assert b"user_a_data" not in response.data


class TestUpdatePathRoute:

    def setup_method(self):
        _clear_all()

    def _seed(self, path_id, token, data):
        client = get_client()
        client.post(
            f"/api/learning-path/{path_id}",
            json=data,
            headers={TOKEN_HEADER: token},
        )

    def test_put_correct_token_returns_200(self):
        token = make_token()
        self._seed("upd-route-1", token, {"step": 1})
        client = get_client()
        response = client.put(
            "/api/learning-path/upd-route-1",
            json={"step": 2},
            headers={TOKEN_HEADER: token},
        )
        assert response.status_code == 200
        assert response.get_json()["path_id"] == "upd-route-1"

    def test_put_actually_updates_stored_data(self):
        token = make_token()
        self._seed("upd-route-2", token, {"v": 1})
        client = get_client()
        client.put(
            "/api/learning-path/upd-route-2",
            json={"v": 99},
            headers={TOKEN_HEADER: token},
        )
        get_resp = client.get(
            "/api/learning-path/upd-route-2",
            headers={TOKEN_HEADER: token},
        )
        assert get_resp.get_json()["data"]["v"] == 99

    def test_put_wrong_token_returns_403(self):
        """A PUT with a wrong token must be rejected with 403."""
        token = make_token()
        self._seed("upd-route-3", token, {})
        client = get_client()
        response = client.put(
            "/api/learning-path/upd-route-3",
            json={"hijacked": True},
            headers={TOKEN_HEADER: make_token()},
        )
        assert response.status_code == 403

    def test_put_wrong_token_does_not_modify_data(self):
        """A rejected PUT must leave the stored data unchanged."""
        token = make_token()
        self._seed("upd-route-4", token, {"original": True})
        client = get_client()
        client.put(
            "/api/learning-path/upd-route-4",
            json={"tampered": True},
            headers={TOKEN_HEADER: make_token()},
        )
        get_resp = client.get(
            "/api/learning-path/upd-route-4",
            headers={TOKEN_HEADER: token},
        )
        data = get_resp.get_json()["data"]
        assert data.get("original") is True
        assert "tampered" not in data

    def test_put_missing_token_returns_400(self):
        token = make_token()
        self._seed("upd-route-5", token, {})
        client = get_client()
        response = client.put(
            "/api/learning-path/upd-route-5",
            json={"x": 1},
        )
        assert response.status_code == 400

    def test_put_nonexistent_path_returns_404(self):
        client = get_client()
        response = client.put(
            "/api/learning-path/no-such",
            json={},
            headers={TOKEN_HEADER: make_token()},
        )
        assert response.status_code == 404

    def test_put_non_json_body_returns_400(self):
        token = make_token()
        self._seed("upd-route-6", token, {})
        client = get_client()
        response = client.put(
            "/api/learning-path/upd-route-6",
            data="bad body",
            content_type="text/plain",
            headers={TOKEN_HEADER: token},
        )
        assert response.status_code == 400


# ---------------------------------------------------------------------------
# Run tests directly (no pytest required)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    test_classes = [
        TestCreateLearningPath,
        TestGetLearningPath,
        TestUpdateLearningPath,
        TestPathExists,
        TestTokenComparison,
        TestCreatePathRoute,
        TestReadPathRoute,
        TestUpdatePathRoute,
    ]

    passed = 0
    failed = 0

    for cls in test_classes:
        instance = cls()
        methods = [m for m in dir(instance) if m.startswith("test_")]
        for method_name in methods:
            if hasattr(instance, "setup_method"):
                instance.setup_method()
            try:
                getattr(instance, method_name)()
                print(f"  PASS  {cls.__name__}.{method_name}")
                passed += 1
            except Exception as exc:
                print(f"  FAIL  {cls.__name__}.{method_name}: {exc}")
                failed += 1

    print(f"\n{passed} passed, {failed} failed out of {passed + failed} tests")
    if failed > 0:
        sys.exit(1)
