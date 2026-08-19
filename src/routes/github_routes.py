import os
import secrets
import requests
from flask import Blueprint, redirect, request, session, jsonify, url_for
from config import Config

github_bp = Blueprint("github", __name__)

GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")

# Session key used to store the OAuth state between login and callback.
_OAUTH_STATE_KEY = "github_oauth_state"

# You can configure your local callback URL in GitHub, e.g., http://localhost:5000/api/github/callback
# In production, it will be your domain.

@github_bp.route("/api/github/login")
def login():
    """Redirect user to GitHub OAuth login."""
    if not GITHUB_CLIENT_ID:
        return jsonify({"error": "GitHub OAuth is not configured on the server."}), 500
        
    # Build the callback URL from the configured base URL instead of the
    # incoming Host header so an attacker cannot poison the redirect target
    # (host-header poisoning) and steal the authorization code.
    state = secrets.token_urlsafe(16)
    session[_OAUTH_STATE_KEY] = state

    redirect_uri = Config.BASE_URL.rstrip('/') + url_for("github.callback")
    auth_url = (
        f"https://github.com/login/oauth/authorize"
        f"?client_id={GITHUB_CLIENT_ID}"
        f"&redirect_uri={redirect_uri}"
        f"&scope=public_repo"
        f"&state={state}"
    )
    return redirect(auth_url)

@github_bp.route("/api/github/callback")
def callback():
    """Handle GitHub OAuth callback and exchange code for access token."""
    code = request.args.get("code")
    if not code:
        return redirect("/?github_auth=error")

    redirect_uri = Config.BASE_URL.rstrip('/') + url_for("github.callback")
    
    token_url = "https://github.com/login/oauth/access_token"
    payload = {
        "client_id": GITHUB_CLIENT_ID,
        "client_secret": GITHUB_CLIENT_SECRET,
        "code": code,
        "redirect_uri": redirect_uri
    }
    headers = {"Accept": "application/json"}

    response = requests.post(token_url, json=payload, headers=headers)
    if response.status_code != 200:
        return redirect("/?github_auth=error")
    try:
        data = response.json()
    except ValueError:
        return redirect("/?github_auth=error")

    access_token = data.get("access_token")
    if access_token:
        session["github_token"] = access_token
        session.permanent = True
        return redirect("/?github_auth=success")
    else:
        return redirect("/?github_auth=error")

@github_bp.route("/api/github/repos")
def repos():
    """Fetch user's repositories using the stored access token."""
    access_token = session.get("github_token")
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
