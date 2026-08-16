# tests/test_recommend_interests.py
# Tests for issue #1835: the hardcoded NO_PROJECT_INTERESTS bypass must not
# block DevOps and Mobile recommendations even though matching projects exist.

import pytest


@pytest.fixture
def client():
    from app import app
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def test_devops_interest_returns_projects(client):
    """Selecting DevOps must return the matching CI/CD project."""
    response = client.post("/api/recommend", json={
        "skills": "Docker",
        "level": "Advanced",
        "interest": "DevOps",
        "time": "High"
    })
    assert response.status_code == 200
    data = response.get_json()
    assert "projects" in data
    assert len(data["projects"]) > 0
    assert any(p.get("interest") == "DevOps" for p in data["projects"])


def test_mobile_interest_returns_projects(client):
    """Selecting Mobile must return the matching Android/Kotlin projects."""
    response = client.post("/api/recommend", json={
        "skills": "Kotlin",
        "level": "Beginner",
        "interest": "Mobile",
        "time": "Low"
    })
    assert response.status_code == 200
    data = response.get_json()
    assert "projects" in data
    assert len(data["projects"]) > 0
    assert any(p.get("interest") == "Mobile" for p in data["projects"])
