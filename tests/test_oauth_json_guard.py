# tests/test_oauth_json_guard.py
# Regression tests for issue #1863: OAuth callbacks must not 500 when
# GitHub returns a non-JSON / non-200 response. They should redirect to
# the auth-error path instead of raising on .json().

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import pytest

from app import app, github


class FakeTokenResponse:
    def __init__(self, status_code, content_type, text):
        self.status_code = status_code
        self.headers = {"Content-Type": content_type}
        self._text = text

    def json(self):
        import json
        return json.loads(self._text)


class FakeAuthlibUserResponse:
    ok = False
    status_code = 502

    def json(self):
        raise ValueError("response is not JSON")


@pytest.fixture
def client():
    app.config["TESTING"] = True
    return app.test_client()


def test_github_callback_html_error_page_redirects(client, monkeypatch):
    def fake_post(url, json=None, headers=None):
        return FakeTokenResponse(502, "text/html", "<html><body>Bad Gateway</body></html>")

    monkeypatch.setattr("requests.post", fake_post)
    response = client.get("/api/github/callback?code=bad", follow_redirects=False)
    assert response.status_code == 302
    assert response.headers["Location"] == "/?github_auth=error"


def test_github_callback_empty_body_redirects(client, monkeypatch):
    def fake_post(url, json=None, headers=None):
        return FakeTokenResponse(200, "application/json", "")

    monkeypatch.setattr("requests.post", fake_post)
    response = client.get("/api/github/callback?code=bad", follow_redirects=False)
    assert response.status_code == 302
    assert response.headers["Location"] == "/?github_auth=error"


def test_github_callback_rate_limited_redirects(client, monkeypatch):
    def fake_post(url, json=None, headers=None):
        return FakeTokenResponse(429, "text/plain", "API rate limit exceeded")

    monkeypatch.setattr("requests.post", fake_post)
    response = client.get("/api/github/callback?code=bad", follow_redirects=False)
    assert response.status_code == 302
    assert response.headers["Location"] == "/?github_auth=error"


def test_authorize_non_ok_user_response_redirects(client, monkeypatch):
    monkeypatch.setattr(github, "authorize_access_token", lambda: {"access_token": "t", "token_type": "bearer"})
    monkeypatch.setattr(github, "get", lambda url, token=None: FakeAuthlibUserResponse())

    response = client.get("/auth/authorize?code=bad", follow_redirects=False)
    assert response.status_code == 302
    assert response.headers["Location"] == "/"


def test_authorize_valid_user_response_redirects_to_profile(client, monkeypatch):
    class GoodResponse:
        ok = True
        status_code = 200

        def json(self):
            return {"id": "github-1863-user", "login": "tester", "avatar_url": "http://a"}

    monkeypatch.setattr(github, "authorize_access_token", lambda: {"access_token": "t", "token_type": "bearer"})
    monkeypatch.setattr(github, "get", lambda url, token=None: GoodResponse())

    with app.app_context():
        from models import db
        response = client.get("/auth/authorize?code=good", follow_redirects=False)
        assert response.status_code == 302
        assert response.headers["Location"].endswith("/profile")


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
