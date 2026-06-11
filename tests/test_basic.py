import sys
import os
import pytest

# Allow imports from project root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils.data_loader import load_all_projects, find_project_by_id, clear_cache, validate_projects
from utils.recommender import (
    get_recommendations,
    validate_recommendation_inputs,
    parse_skills,
    score_single_project,
    SCORING_WEIGHTS
)
from app import app


# ============================================================
# Setup
# ============================================================

def setup_module():
    clear_cache()


# ============================================================
# Data Loader Tests
# ============================================================

def test_projects_json_loads():
    projects = load_all_projects()
    assert isinstance(projects, list)
    assert len(projects) > 0


def test_find_project_by_id():
    project = find_project_by_id(1)
    assert project is not None
    assert project["id"] == 1


def test_find_project_by_id_missing():
    assert find_project_by_id(99999) is None


# ============================================================
# Recommender Tests
# ============================================================

def test_parse_skills():
    assert parse_skills("Python, HTML") == ["python", "html"]
    assert parse_skills("") == []


def test_score_project():
    project = {
        "skills": ["Python"],
        "level": "Beginner",
        "interest": "Data",
        "time": "Low"
    }

    score = score_single_project(
        project,
        user_skills=["python"],
        level="Beginner",
        interest="Data",
        time_availability="Low"
    )

    assert score > 0


def test_get_recommendations():
    results = get_recommendations("Python", "Beginner", "Data", "Low")

    assert isinstance(results, dict)
    assert "recommendations" in results
    assert isinstance(results["recommendations"], list)


# ============================================================
# Input Validation Tests
# ============================================================

def test_validate_inputs():
    errors = validate_recommendation_inputs("Python", "Beginner", "Data", "Low")
    assert errors == []


def test_validate_missing_fields():
    errors = validate_recommendation_inputs("", "", "", "")
    assert len(errors) == 4


# ============================================================
# Flask Route Tests
# ============================================================

def get_client():
    app.config["TESTING"] = True
    return app.test_client()


def test_home_route():
    client = get_client()
    response = client.get("/")
    assert response.status_code == 200


def test_recommend_api():
    client = get_client()
    response = client.post("/api/recommend", json={
        "skills": "Python",
        "level": "Beginner",
        "interest": "Data",
        "time": "Low"
    })

    assert response.status_code == 200
    data = response.get_json()
    assert "projects" in data


def test_project_not_found():
    client = get_client()
    response = client.get("/project/99999")
    assert response.status_code == 404


def test_health():
    client = get_client()
    response = client.get("/health")
    assert response.status_code == 200