# tests/conftest.py
# Pytest configuration and shared fixtures for DevPath tests.

import sys
import os

# Allow imports from the project root and src/ when running tests
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import pytest
from app import app
from utils.rate_limiter import reset_rate_limits


@pytest.fixture
def client():
    """Provide a Flask test client for testing the application."""
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    with app.test_client() as client:
        yield client


@pytest.fixture(autouse=True)
def _reset_rate_limiter_state():
    """Clear rate-limit counters before every test.
 
    Without this, tests across different files that hit the same rate-limited route 
    would exhaust each other's request budget depending on test execution order, causing
    order-dependent 429 failures unrelated to what each test is actually checking.
    """
    reset_rate_limits()
    yield