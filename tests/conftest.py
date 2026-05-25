# tests/conftest.py
# Pytest configuration and shared fixtures for DevPath tests.

import sys
import os

# Allow imports from the project root when running tests
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from app import app


@pytest.fixture
def client():
    """Provide a Flask test client for testing the application."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client
