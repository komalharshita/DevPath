# tests/test_payload_size_limit.py
# Tests for Issue #1137: _MAX_DATA_BYTES enforcement on learning-path endpoints.

import json
import secrets
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from utils.learning_path import _clear_all
from app import app

TOKEN_HEADER = "X-Learning-Path-Token"
MAX_BYTES = 64 * 1024  # must match _MAX_DATA_BYTES in main_routes.py


def make_token():
    return secrets.token_urlsafe(32)


def get_client():
    app.config["TESTING"] = True
    return app.test_client()


def _payload_of_size(target_bytes: int) -> bytes:
    """
    Build a JSON object whose encoded byte length equals target_bytes.

    The envelope {"k": "<value>"} is 8 bytes of overhead; the rest is filled
    with the string value so the total serialised length hits the target.
    """
    overhead = len(b'{"k": ""}')
    value_len = max(0, target_bytes - overhead)
    obj = {"k": "x" * value_len}
    encoded = json.dumps(obj).encode("utf-8")
    # Trim or pad to hit the exact byte count (json.dumps output is predictable here)
    return encoded


def _post(client, path_id, raw_body: bytes, token=None):
    return client.post(
        f"/api/learning-path/{path_id}",
        data=raw_body,
        content_type="application/json",
        headers={TOKEN_HEADER: token or make_token()},
    )


def _put(client, path_id, raw_body: bytes, token=None):
    return client.put(
        f"/api/learning-path/{path_id}",
        data=raw_body,
        content_type="application/json",
        headers={TOKEN_HEADER: token or make_token()},
    )


# ---------------------------------------------------------------------------
# POST (create) — size enforcement
# ---------------------------------------------------------------------------

class TestCreatePayloadSizeLimit:

    def setup_method(self):
        _clear_all()

    def test_create_small_payload_accepted(self):
        """Regression for Issue #1137: a normal-sized payload must be accepted."""
        client = get_client()
        response = client.post(
            "/api/learning-path/small-create",
            json={"step": 1, "done": False},
            headers={TOKEN_HEADER: make_token()},
        )
        assert response.status_code == 201

    def test_create_payload_below_limit_accepted(self):
        """Payload strictly below the 64 KB limit must be stored."""
        body = _payload_of_size(MAX_BYTES - 100)
        client = get_client()
        response = _post(client, "below-limit", body)
        assert response.status_code == 201

    def test_create_payload_exactly_at_limit_accepted(self):
        """Payload whose byte count equals exactly _MAX_DATA_BYTES must be accepted."""
        body = _payload_of_size(MAX_BYTES)
        client = get_client()
        response = _post(client, "exact-limit", body)
        assert response.status_code == 201

    def test_create_payload_above_limit_rejected(self):
        """Regression for Issue #1137: POST with oversized payload must return 400."""
        body = _payload_of_size(MAX_BYTES + 1)
        client = get_client()
        response = _post(client, "over-limit-create", body)
        assert response.status_code == 400

    def test_create_oversized_response_contains_error_key(self):
        """Rejected response must include an 'error' key."""
        body = _payload_of_size(MAX_BYTES + 1)
        client = get_client()
        response = _post(client, "over-err-key", body)
        assert "error" in response.get_json()

    def test_create_oversized_error_mentions_64kb(self):
        """Error message must mention the 64 KB limit."""
        body = _payload_of_size(MAX_BYTES + 1)
        client = get_client()
        response = _post(client, "over-64kb-msg", body)
        error_text = response.get_json()["error"].lower()
        assert "64" in error_text

    def test_create_oversized_not_stored(self):
        """An oversized POST must not persist any data."""
        from utils.learning_path import path_exists
        body = _payload_of_size(MAX_BYTES + 1)
        client = get_client()
        _post(client, "no-store-create", body)
        assert not path_exists("no-store-create")

    def test_create_nested_json_below_limit_accepted(self):
        """A nested JSON object within the size limit must be accepted."""
        client = get_client()
        payload = {"levels": [{"id": i, "done": False} for i in range(50)]}
        response = client.post(
            "/api/learning-path/nested-create",
            json=payload,
            headers={TOKEN_HEADER: make_token()},
        )
        assert response.status_code == 201

    def test_create_large_nested_json_rejected(self):
        """A deeply nested JSON object exceeding the limit must be rejected."""
        client = get_client()
        large_payload = {"steps": ["x" * 100 for _ in range(700)]}
        encoded = json.dumps(large_payload).encode("utf-8")
        assert len(encoded) > MAX_BYTES, "Test payload not large enough; adjust size"
        response = _post(client, "nested-over", encoded)
        assert response.status_code == 400


# ---------------------------------------------------------------------------
# PUT (update) — size enforcement
# ---------------------------------------------------------------------------

class TestUpdatePayloadSizeLimit:

    def setup_method(self):
        _clear_all()

    def _seed(self, path_id, token, data=None):
        client = get_client()
        client.post(
            f"/api/learning-path/{path_id}",
            json=data or {"step": 1},
            headers={TOKEN_HEADER: token},
        )
        return client

    def test_update_small_payload_accepted(self):
        """A normal-sized PUT payload must be accepted."""
        token = make_token()
        client = self._seed("small-update", token)
        response = client.put(
            "/api/learning-path/small-update",
            json={"step": 2},
            headers={TOKEN_HEADER: token},
        )
        assert response.status_code == 200

    def test_update_payload_below_limit_accepted(self):
        """PUT payload strictly below 64 KB must succeed."""
        token = make_token()
        client = self._seed("upd-below", token)
        body = _payload_of_size(MAX_BYTES - 100)
        response = _put(client, "upd-below", body, token=token)
        assert response.status_code == 200

    def test_update_payload_exactly_at_limit_accepted(self):
        """PUT payload equal to exactly _MAX_DATA_BYTES must succeed."""
        token = make_token()
        client = self._seed("upd-exact", token)
        body = _payload_of_size(MAX_BYTES)
        response = _put(client, "upd-exact", body, token=token)
        assert response.status_code == 200

    def test_update_payload_above_limit_rejected(self):
        """Regression for Issue #1137: PUT with oversized payload must return 400."""
        token = make_token()
        client = self._seed("upd-over", token)
        body = _payload_of_size(MAX_BYTES + 1)
        response = _put(client, "upd-over", body, token=token)
        assert response.status_code == 400

    def test_update_oversized_response_contains_error_key(self):
        """Rejected PUT response must include an 'error' key."""
        token = make_token()
        client = self._seed("upd-err-key", token)
        body = _payload_of_size(MAX_BYTES + 1)
        response = _put(client, "upd-err-key", body, token=token)
        assert "error" in response.get_json()

    def test_update_oversized_error_mentions_64kb(self):
        """PUT error message must mention the 64 KB limit."""
        token = make_token()
        client = self._seed("upd-64msg", token)
        body = _payload_of_size(MAX_BYTES + 1)
        response = _put(client, "upd-64msg", body, token=token)
        error_text = response.get_json()["error"].lower()
        assert "64" in error_text

    def test_update_oversized_does_not_overwrite_stored_data(self):
        """A rejected PUT must leave the original data intact."""
        from utils.learning_path import get_learning_path
        token = make_token()
        client = self._seed("upd-intact", token, data={"original": True})
        body = _payload_of_size(MAX_BYTES + 1)
        _put(client, "upd-intact", body, token=token)
        stored = get_learning_path("upd-intact", token)
        assert stored == {"original": True}

    def test_update_nested_json_below_limit_accepted(self):
        """Nested JSON within the size limit must succeed on PUT."""
        token = make_token()
        client = self._seed("upd-nested", token)
        payload = {"milestones": [{"id": i, "label": f"step-{i}"} for i in range(30)]}
        response = client.put(
            "/api/learning-path/upd-nested",
            json=payload,
            headers={TOKEN_HEADER: token},
        )
        assert response.status_code == 200
