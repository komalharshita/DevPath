# tests/test_secret_key.py
# Tests for the SECRET_KEY handling (issue #1815).
#
# Previously SECRET_KEY was defined twice in config.py with two different
# public defaults, app.py set a third fallback that was immediately
# overwritten, and the app booted in production with a publicly-known signing
# key.  Now there is one definition and the app refuses to start (outside
# debug mode) with a missing or known-default key.

import sys
import os

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from config import secret_key_is_safe, KNOWN_DEFAULT_SECRET_KEYS

from app import app
import app as app_module


# ============================================================
# secret_key_is_safe unit tests
# ============================================================

def test_known_defaults_are_rejected():
    for default in KNOWN_DEFAULT_SECRET_KEYS:
        assert secret_key_is_safe(default) is False


def test_missing_and_empty_keys_are_rejected():
    assert secret_key_is_safe(None) is False
    assert secret_key_is_safe("") is False


def test_secure_random_key_is_accepted():
    assert secret_key_is_safe("a-secure-random-64-char-secret-0123456789abcdef") is True


# ============================================================
# Effective configuration tests
# ============================================================

def test_effective_secret_key_is_not_a_default():
    """The key the app actually signs with must not be a known default."""
    value = app.config.get("SECRET_KEY")
    assert value, "SECRET_KEY must be configured"
    assert value not in KNOWN_DEFAULT_SECRET_KEYS


def test_only_one_secret_key_definition_in_config():
    """config.py must define SECRET_KEY exactly once (no dead duplicate)."""
    import inspect
    import config

    source = inspect.getsource(config)
    occurrences = source.count("SECRET_KEY = os.getenv(\"SECRET_KEY\"")
    assert occurrences == 1, f"Expected 1 SECRET_KEY definition, found {occurrences}"


# ============================================================
# Startup guard tests
# ============================================================

def test_guard_raises_for_known_default_key(monkeypatch):
    """In non-debug mode a known-default key must make startup refuse to run."""
    monkeypatch.setenv("FLASK_DEBUG", "0")
    original = app.config.get("SECRET_KEY")
    app.config["SECRET_KEY"] = "dev_secret_key_change_in_production"
    try:
        with pytest.raises(RuntimeError, match="SECRET_KEY"):
            app_module._validate_secret_key()
    finally:
        app.config["SECRET_KEY"] = original


def test_guard_raises_for_missing_key(monkeypatch):
    monkeypatch.setenv("FLASK_DEBUG", "0")
    original = app.config.get("SECRET_KEY")
    app.config["SECRET_KEY"] = ""
    try:
        with pytest.raises(RuntimeError, match="SECRET_KEY"):
            app_module._validate_secret_key()
    finally:
        app.config["SECRET_KEY"] = original


def test_guard_passes_for_secure_key(monkeypatch):
    """A strong key must allow startup even in non-debug mode."""
    monkeypatch.setenv("FLASK_DEBUG", "0")
    original = app.config.get("SECRET_KEY")
    app.config["SECRET_KEY"] = "a-secure-random-secret-key"
    try:
        # Must not raise.
        app_module._validate_secret_key()
    finally:
        app.config["SECRET_KEY"] = original


def test_guard_allows_default_key_in_debug_mode(monkeypatch):
    """Development (FLASK_DEBUG) may still use the default key."""
    monkeypatch.setenv("FLASK_DEBUG", "1")
    original = app.config.get("SECRET_KEY")
    app.config["SECRET_KEY"] = "dev_secret_key_change_in_production"
    try:
        # Must not raise.
        app_module._validate_secret_key()
    finally:
        app.config["SECRET_KEY"] = original
