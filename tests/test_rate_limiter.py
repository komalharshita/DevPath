# tests/test_rate_limiter.py
# Tests for the in-memory sliding-window rate limiter.
#
# Tests:
#   - Requests within the limit succeed
#   - The request that exceeds the limit returns 429
#   - Routes without the decorator are unaffected
#   - Different client IPs are tracked independently
#   - reset_rate_limits() clears state between tests

import pytest
from flask import Flask

from utils.rate_limiter import rate_limit, reset_rate_limits



# Fixtures

@pytest.fixture
def app():
    """Minimal Flask app with one rate-limited test route."""
    app = Flask(__name__)

    @app.route("/limited")
    @rate_limit(max_requests=3, window_seconds=60)
    def limited():
        return "ok", 200

    @app.route("/unlimited")
    def unlimited():
        return "ok", 200

    yield app
    reset_rate_limits()  # don't leak state into the next test


@pytest.fixture
def client(app):
    return app.test_client()


# Core limiting behavior

def test_requests_within_limit_succeed(client):
    """The first N requests (N = max_requests) should all succeed."""
    for _ in range(3):
        resp = client.get("/limited")
        assert resp.status_code == 200


def test_request_over_limit_returns_429(client):
    """The (N+1)th request in the window should be rejected with 429."""
    for _ in range(3):
        client.get("/limited")

    resp = client.get("/limited")
    assert resp.status_code == 429


def test_unrelated_route_is_not_rate_limited(client):
    """A route without the decorator should be unaffected."""
    for _ in range(10):
        resp = client.get("/unlimited")
        assert resp.status_code == 200


# Per-client isolation

def test_different_clients_have_independent_limits(app):
    """Two different client IPs should not share the same counter."""
    client_a = app.test_client()
    client_b = app.test_client()

    for _ in range(3):
        resp = client_a.get("/limited", environ_overrides={"REMOTE_ADDR": "1.1.1.1"})
        assert resp.status_code == 200

    # Client A is now at its limit...
    resp = client_a.get("/limited", environ_overrides={"REMOTE_ADDR": "1.1.1.1"})
    assert resp.status_code == 429

    # ...but client B should still be allowed.
    resp = client_b.get("/limited", environ_overrides={"REMOTE_ADDR": "2.2.2.2"})
    assert resp.status_code == 200


# State reset

def test_reset_rate_limits_clears_state(client):
    """reset_rate_limits() should allow a previously-blocked client through again."""
    for _ in range(3):
        client.get("/limited")
    assert client.get("/limited").status_code == 429

    reset_rate_limits()

    assert client.get("/limited").status_code == 200