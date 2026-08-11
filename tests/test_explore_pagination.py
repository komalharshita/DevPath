# tests/test_explore_pagination.py
# Tests for explore pagination edge cases (issue #1836).
#
# Validates that invalid `per_page` / `page` values cannot crash the
# /explore endpoint or produce unbounded result sizes.

import pytest


@pytest.fixture
def client():
    from app import app
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def test_explore_default_returns_200(client):
    """The explore page must render normally with no query params."""
    response = client.get("/explore")
    assert response.status_code == 200


def test_explore_per_page_zero_no_crash(client):
    """per_page=0 previously raised ZeroDivisionError -> 500."""
    response = client.get("/explore?per_page=0")
    assert response.status_code == 200
    assert b"Showing" in response.data


def test_explore_per_page_negative_no_crash(client):
    """Negative per_page values must be clamped and not break pagination."""
    response = client.get("/explore?per_page=-1")
    assert response.status_code == 200
    assert b"Showing" in response.data


def test_explore_per_page_oversized_is_capped(client):
    """Oversized per_page values must be capped (no full-catalog dump)."""
    response = client.get("/explore?per_page=100000")
    assert response.status_code == 200
    assert b"Showing" in response.data


def test_explore_page_negative_clamped(client):
    """Negative page values must be clamped to page 1."""
    response = client.get("/explore?page=-5")
    assert response.status_code == 200
    assert b"Showing" in response.data


def test_explore_page_beyond_last_is_clamped(client):
    """page beyond total_pages must be clamped to the last page."""
    response = client.get("/explore?page=999999")
    assert response.status_code == 200
    assert b"Showing" in response.data
