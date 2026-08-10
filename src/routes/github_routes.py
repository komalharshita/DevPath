import requests
from flask import Blueprint, redirect, session, jsonify, url_for

github_bp = Blueprint("github", __name__)

# This blueprint previously ran a second, manual OAuth flow
# (/api/github/login + /api/github/callback) that was incompatible with the
# Authlib flow in routes/auth_routes.py:
#
#   - it stored a bare access-token *string* in session['github_token'],
#     while the Authlib flow stores the full token dict
#     {"access_token": ..., "token_type": ..., "expires_in": ...}, and
#     export_github expects the dict shape -> TypeError.
#   - it never created a User row nor set session['user_id'], so the user
#     remained unauthenticated for /profile and progress APIs.
#   - it read credentials from os.getenv at import time instead of Config.
#
# Both OAuth entry points now delegate to the single Authlib flow, so every
# login produces one consistent session payload.  Only /api/github/repos
# remains here (used by the frontend to list the user's repositories).


def _session_access_token():
    """Return the GitHub access token from the session, if present.

    The Authlib flow stores the full token dict.  A bare string may still
    exist in older sessions, so both shapes are handled defensively.
    """
    token = session.get("github_token")
    if isinstance(token, dict):
        return token.get("access_token")
    if isinstance(token, str) and token:
        return token
    return None


@github_bp.route("/api/github/login")
def login():
    """Alias of the canonical Authlib login flow.

    Kept so existing frontend links (and bookmarks) keep working while the
    app consolidates on a single OAuth implementation.
    """
    return redirect(url_for("auth.login"))


@github_bp.route("/api/github/callback")
def callback():
    """Backward-compatible alias of the canonical Authlib callback.

    Old GitHub OAuth app redirect URIs may still point here; forward the
    user into the canonical flow rather than returning a 404.
    """
    return redirect(url_for("auth.login"))


@github_bp.route("/api/github/repos")
def repos():
    """Fetch user's repositories using the stored access token."""
    access_token = _session_access_token()
    if not access_token:
        return jsonify({"error": "Not authenticated with GitHub"}), 401

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/vnd.github.v3+json"
    }

    response = requests.get("https://api.github.com/user/repos?sort=updated&per_page=100", headers=headers)

    if response.status_code != 200:
        return jsonify({"error": "Failed to fetch repositories from GitHub"}), response.status_code

    return jsonify(response.json()), 200
