# tests/test_explore_interests.py
# Tests for issue #1840: the /explore interest dropdown must be generated
# from the real dataset instead of a hardcoded list that includes interests
# with no matching projects.

import pytest


@pytest.fixture
def client():
    from app import app
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def test_explore_dropdown_includes_real_interests(client):
    """The dropdown must offer interests that exist in the dataset."""
    response = client.get("/explore")
    assert response.status_code == 200
    assert b"Automation" in response.data
    assert b"DevOps" in response.data
    assert b"Mobile" in response.data
    assert b"Backend" in response.data


def test_explore_dropdown_omits_interests_without_projects(client):
    """Options like 'Business Logic' with no matching projects must be gone."""
    response = client.get("/explore")
    assert response.status_code == 200
    assert b"Business Logic" not in response.data
    assert b"Machine Learning/AI" not in response.data
