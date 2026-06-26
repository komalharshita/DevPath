# tests/test_recent_recommendations.py
# Regression tests for issue #770 — Recent Recommendations History.
# Ensures all required DOM containers and buttons are present in the homepage HTML.

import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def test_recent_recommendations_section_exists(client):
    """The homepage HTML must include the recent-recommendations-section container."""
    response = client.get("/")
    assert response.status_code == 200
    html = response.data.decode("utf-8")
    assert 'id="recent-recommendations-section"' in html, (
        "The element #recent-recommendations-section is missing from the index.html page."
    )


def test_recent_recommendations_list_exists(client):
    """The homepage HTML must include the recent-recommendations-list container."""
    response = client.get("/")
    assert response.status_code == 200
    html = response.data.decode("utf-8")
    assert 'id="recent-recommendations-list"' in html, (
        "The element #recent-recommendations-list is missing from the index.html page."
    )


def test_clear_history_btn_exists(client):
    """The homepage HTML must include the clear-history-btn button."""
    response = client.get("/")
    assert response.status_code == 200
    html = response.data.decode("utf-8")
    assert 'id="clear-history-btn"' in html, (
        "The element #clear-history-btn is missing from the index.html page."
    )
