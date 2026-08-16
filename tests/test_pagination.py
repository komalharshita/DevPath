import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from utils.pagination import parse_pagination, DEFAULT_PER_PAGE, MAX_PER_PAGE

from app import app


def get_client():
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False
    return app.test_client()


# ============================================================
# parse_pagination helper unit tests
# ============================================================

def test_parse_pagination_defaults():
    """Missing values fall back to (1, DEFAULT_PER_PAGE)."""
    assert parse_pagination(None, None) == (1, DEFAULT_PER_PAGE)


def test_parse_pagination_valid_values_passthrough():
    assert parse_pagination(3, 10) == (3, 10)


def test_parse_pagination_zero_per_page():
    """per_page=0 would have caused ZeroDivisionError - must be clamped to 1."""
    assert parse_pagination(1, 0) == (1, 1)


def test_parse_pagination_negative_per_page():
    assert parse_pagination(1, -5) == (1, 1)


def test_parse_pagination_huge_per_page_clamped():
    """per_page above MAX_PER_PAGE must be clamped, not accepted."""
    assert parse_pagination(1, 100000) == (1, MAX_PER_PAGE)


def test_parse_pagination_zero_page():
    assert parse_pagination(0, 12) == (1, 12)


def test_parse_pagination_negative_page():
    assert parse_pagination(-3, 12) == (1, 12)


# ============================================================
# /explore integration tests
# ============================================================

def test_explore_per_page_zero_never_500():
    """per_page=0 previously raised ZeroDivisionError -> must now return 200."""
    response = get_client().get("/explore?per_page=0")
    assert response.status_code == 200


def test_explore_per_page_negative():
    response = get_client().get("/explore?per_page=-5")
    assert response.status_code == 200


def test_explore_per_page_huge_clamped():
    """A huge per_page must be clamped to MAX_PER_PAGE and still render."""
    response = get_client().get("/explore?per_page=100000")
    assert response.status_code == 200


def test_explore_page_zero():
    response = get_client().get("/explore?page=0")
    assert response.status_code == 200


def test_explore_page_negative():
    response = get_client().get("/explore?page=-3")
    assert response.status_code == 200


def test_explore_all_bad_params_combination():
    """A combination of every malformed value must never produce a 500."""
    response = get_client().get("/explore?page=-2&per_page=0&search=&level=")
    assert response.status_code == 200


def test_explore_render_is_bounded_by_per_page():
    """The rendered page must not contain more cards than the requested per_page."""
    response = get_client().get("/explore?per_page=5")
    assert response.status_code == 200
    card_count = response.data.count(b'class="project-card"')
    assert 0 < card_count <= 5
