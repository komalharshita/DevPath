"""
jwt_auth_api.py
===============
Project:    REST API with JWT Authentication (starter)
Stack:      Flask, PyJWT, bcrypt, JSON

What you will build:
    A small REST API where users register with a hashed password, log in to
    receive a signed JWT, and access protected routes by sending
    Authorization: Bearer <token>.

How to run (from the starter_code directory):
    pip install -r jwt_requirements.txt
    python jwt_auth_api.py

Then test with curl or Postman (register -> login -> protected GET with header).

Learning goals:
    - Storing password hashes (never plain text) with bcrypt
    - Issuing and verifying JWTs with an expiry claim
    - Protecting routes with a decorator or before_request hook
    - Refresh tokens or logout strategies (optional stretch goals)

Security notes:
    - Use a strong random SECRET_KEY in production (env var JWT_SECRET_KEY).
    - Use HTTPS in production; JWTs in headers over HTTP are vulnerable to MITM.
"""

import os
from functools import wraps
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from flask import Flask, jsonify, request

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY", "dev-only-change-me")

# In-memory user store for the exercise — replace with a database for production.
USERS = {}  # username -> {"password_hash": bytes, "created_at": str}

JWT_ALGORITHM = "HS256"
TOKEN_HOURS = 24


def utc_now():
    return datetime.now(timezone.utc)


def token_required(view_fn):
    """Verify Bearer JWT and pass `username` (from claim sub) into the view."""

    @wraps(view_fn)
    def wrapped(*args, **kwargs):
        auth = request.headers.get("Authorization", "")
        if not auth.startswith("Bearer "):
            return jsonify({"error": "Authorization header must be: Bearer <token>"}), 401
        token = auth[7:].strip()
        if not token:
            return jsonify({"error": "Missing token."}), 401
        try:
            payload = jwt.decode(
                token,
                app.config["SECRET_KEY"],
                algorithms=[JWT_ALGORITHM],
            )
            username = payload.get("sub")
            if not username or not isinstance(username, str):
                return jsonify({"error": "Invalid token payload."}), 401
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token has expired."}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid or malformed token."}), 401
        return view_fn(username, *args, **kwargs)

    return wrapped


@app.route("/", methods=["GET"])
def health():
    return jsonify({
        "status": "running",
        "message": "JWT Auth API — register, then login, then GET /profile with Bearer token.",
        "endpoints": {
            "register": "POST /register  JSON: {\"username\", \"password\"}",
            "login": "POST /login       JSON: {\"username\", \"password\"}",
            "profile": "GET /profile     Header: Authorization: Bearer <jwt>",
        },
    }), 200


@app.route("/register", methods=["POST"])
def register():
    """POST /register — create a user with bcrypt-hashed password."""
    data = request.get_json(silent=True)
    if not data or not isinstance(data, dict):
        return jsonify({"error": "JSON body required."}), 400

    username = (data.get("username") or "").strip()
    password = data.get("password") or ""

    if not username:
        return jsonify({"error": "username is required."}), 400
    if len(username) < 3 or len(username) > 64:
        return jsonify({"error": "username must be between 3 and 64 characters."}), 400
    if not password:
        return jsonify({"error": "password is required."}), 400
    if len(password) < 8:
        return jsonify({"error": "password must be at least 8 characters."}), 400

    if username in USERS:
        return jsonify({"error": "Username already taken."}), 409

    pw_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    USERS[username] = {
        "password_hash": pw_hash,
        "created_at": utc_now().isoformat(),
    }
    return jsonify({"message": "User created."}), 201


@app.route("/login", methods=["POST"])
def login():
    """POST /login — verify password and return a JWT."""
    data = request.get_json(silent=True)
    if not data or not isinstance(data, dict):
        return jsonify({"error": "JSON body required."}), 400

    username = (data.get("username") or "").strip()
    password = data.get("password") or ""

    if not username or not password:
        return jsonify({"error": "username and password are required."}), 400

    user = USERS.get(username)
    if not user:
        return jsonify({"error": "Invalid username or password."}), 401

    if not bcrypt.checkpw(password.encode("utf-8"), user["password_hash"]):
        return jsonify({"error": "Invalid username or password."}), 401

    expires = utc_now() + timedelta(hours=TOKEN_HOURS)
    payload = {
        "sub": username,
        "exp": expires,
        "iat": utc_now(),
    }
    token = jwt.encode(payload, app.config["SECRET_KEY"], algorithm=JWT_ALGORITHM)
    if isinstance(token, bytes):
        token = token.decode("utf-8")
    return jsonify({"access_token": token, "token_type": "Bearer"}), 200


@app.route("/profile", methods=["GET"])
@token_required
def profile(username):
    """GET /profile — requires Authorization: Bearer <jwt>."""
    if username not in USERS:
        return jsonify({"error": "User no longer exists."}), 404
    return jsonify({"username": username}), 200


if __name__ == "__main__":
    print("JWT Auth API on http://127.0.0.1:5000")
    app.run(debug=True)
