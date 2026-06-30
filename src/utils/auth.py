# utils/auth.py
# DB-backed auth for DevPath using SQLite.
#
# Two tables:
#   users    — username, password hash, salt, path_id
#   sessions — token, username (survives server restarts)
#
# Public surface (unchanged):
#   register_user(username, password)  -> token (str)
#   login_user(username, password)     -> token (str)
#   get_user_from_token(token)         -> username (str) or None
#   get_user_path_id(username)         -> path_id (str) or None
#   logout_user(token)                 -> None
#
# Errors:
#   AuthError — username taken, bad credentials, etc.

import hashlib
import secrets
import sqlite3
import os

from config import Config

class AuthError(Exception):
    pass

# DB file sits next to src/ so it's not inside the package
_DB_PATH = os.getenv(
    "DEVPATH_DB",
    os.path.join(os.path.dirname(__file__), "..", "..", "devpath.db")
)

def _connect():
    """Open a new SQLite connection with row access by column name."""
    conn = sqlite3.connect(_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def _init_db():
    """Create the users and sessions tables if they don't already exist."""
    with _connect() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                pw_hash  TEXT NOT NULL,
                salt     TEXT NOT NULL,
                path_id  TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                token    TEXT PRIMARY KEY,
                username TEXT NOT NULL
            )
        """)
        conn.commit()

# init on import
_init_db()

def _hash_password(password, salt):
    """Hash a password with the given salt using PBKDF2-HMAC-SHA256."""
    return hashlib.pbkdf2_hmac(
        "sha256", password.encode(), salt.encode(), 100_000
    ).hex()

def register_user(username, password):
    """Create a new account and return a fresh session token.

    Validates username/password length, hashes the password with a random
    salt, assigns the user a unique learning-path ID, and opens a session.
    Raises AuthError if validation fails or the username is already taken.
    """
    username = (username or "").strip().lower()
    password = (password or "").strip()

    if not username or len(username) < 2:
        raise AuthError("Username must be at least 2 characters.")
    if not password or len(password) < 4:
        raise AuthError("Password must be at least 4 characters.")

    salt    = secrets.token_hex(16)
    pw_hash = _hash_password(password, salt)
    path_id = "user-" + secrets.token_urlsafe(16)
    token   = secrets.token_urlsafe(32)

    try:
        with _connect() as conn:
            conn.execute(
                "INSERT INTO users (username, pw_hash, salt, path_id) "
                "VALUES (?, ?, ?, ?)",
                (username, pw_hash, salt, path_id)
            )
            conn.execute(
                "INSERT INTO sessions (token, username) VALUES (?, ?)",
                (token, username)
            )
            conn.commit()
    except sqlite3.IntegrityError:
        raise AuthError("Username already taken.")

    return token

def login_user(username, password):
    """Validate credentials and return a fresh session token.

    Raises AuthError with a generic "invalid username or password" message
    on either a missing user or a wrong password, so failed attempts can't
    be used to enumerate which usernames exist.
    """
    username = (username or "").strip().lower()
    password = (password or "").strip()

    with _connect() as conn:
        row = conn.execute(
            "SELECT pw_hash, salt FROM users WHERE username = ?", (username,)
        ).fetchone()

    if not row:
        raise AuthError("Invalid username or password.")

    pw_hash = _hash_password(password, row["salt"])
    if not secrets.compare_digest(pw_hash, row["pw_hash"]):
        raise AuthError("Invalid username or password.")

    token = secrets.token_urlsafe(32)
    with _connect() as conn:
        conn.execute(
            "INSERT INTO sessions (token, username) VALUES (?, ?)", (token, username)
        )
        conn.commit()

    return token

def get_user_from_token(token):
    """Return the username tied to a session token, or None if invalid."""
    if not token:
        return None
    with _connect() as conn:
        row = conn.execute(
            "SELECT username FROM sessions WHERE token = ?", (token,)
        ).fetchone()
    return row["username"] if row else None

def get_user_path_id(username):
    """Return the server-side learning-path ID for a user, or None."""
    if not username:
        return None
    with _connect() as conn:
        row = conn.execute(
            "SELECT path_id FROM users WHERE username = ?",
            ((username or "").strip().lower(),)
        ).fetchone()
    return row["path_id"] if row else None

def logout_user(token):
    """Delete the session for a token, if it exists. No-op on empty token."""
    if not token:
        return
    with _connect() as conn:
        conn.execute("DELETE FROM sessions WHERE token = ?", (token,))
        conn.commit()
