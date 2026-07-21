# tests/test_case_sensitivity.py
# Regression tests for Issue #1130: case-insensitive skill matching.

import pytest
from utils.recommender import _normalize_skill, parse_skills, score_single_project, get_recommendations

# ---------------------------------------------------------------------------
# _normalize_skill
# ---------------------------------------------------------------------------

def test_normalize_skill_lowercase():
    assert _normalize_skill("python") == "python"

def test_normalize_skill_uppercase():
    assert _normalize_skill("PYTHON") == "python"

def test_normalize_skill_mixed_case():
    assert _normalize_skill("PyThOn") == "python"

def test_normalize_skill_leading_whitespace():
    assert _normalize_skill(" python") == "python"

def test_normalize_skill_trailing_whitespace():
    assert _normalize_skill("python ") == "python"

def test_normalize_skill_surrounding_whitespace():
    assert _normalize_skill(" python ") == "python"

def test_normalize_skill_uppercase_with_whitespace():
    assert _normalize_skill("  PYTHON  ") == "python"

# ---------------------------------------------------------------------------
# parse_skills — case and whitespace normalization
# ---------------------------------------------------------------------------

def test_parse_skills_exact_lowercase():
    assert parse_skills("python") == ["python"]

def test_parse_skills_uppercase():
    assert parse_skills("PYTHON") == ["python"]

def test_parse_skills_mixed_case():
    assert parse_skills("PyThOn") == ["python"]

def test_parse_skills_leading_whitespace():
    assert parse_skills(" python") == ["python"]

def test_parse_skills_trailing_whitespace():
    assert parse_skills("python ") == ["python"]

def test_parse_skills_surrounding_whitespace():
    assert parse_skills(" python ") == ["python"]

def test_parse_skills_multiple_skills_uppercase():
    assert parse_skills("PYTHON, HTML") == ["python", "html"]

def test_parse_skills_multiple_skills_mixed_case():
    assert parse_skills("Python, JavaScript") == ["python", "javascript"]

def test_parse_skills_whitespace_around_commas():
    assert parse_skills("  python  ,  html  ") == ["python", "html"]

def test_parse_skills_json_array_uppercase():
    assert parse_skills('["PYTHON", "HTML"]') == ["python", "html"]

def test_parse_skills_json_array_mixed_case():
    assert parse_skills('["Python", "JavaScript"]') == ["python", "javascript"]

def test_parse_skills_json_array_with_whitespace():
    assert parse_skills('[" Python ", " HTML "]') == ["python", "html"]

# ---------------------------------------------------------------------------
# score_single_project — project tag normalization
# ---------------------------------------------------------------------------

_BEGINNER_DATA_LOW = dict(level="beginner", interest="data", time_availability="low")


def _make_project(**kwargs):
    defaults = {
        "id": 999,
        "title": "Test Project",
        "skills": ["Python"],
        "level": "Beginner",
        "interest": "Data",
        "time": "Low",
    }
    defaults.update(kwargs)
    return defaults


def test_score_exact_match():
    project = _make_project(skills=["python"])
    score = score_single_project(project, ["python"], **_BEGINNER_DATA_LOW)
    assert score > 0


def test_score_lowercase_user_vs_capitalized_tag():
    """Issue #1130 regression: lowercase input must match capitalized project tag."""
    project = _make_project(skills=["Python"])
    score = score_single_project(project, ["python"], **_BEGINNER_DATA_LOW)
    assert score > 0


def test_score_uppercase_user_input():
    project = _make_project(skills=["Python"])
    user_skills = parse_skills("PYTHON")
    score = score_single_project(project, user_skills, **_BEGINNER_DATA_LOW)
    assert score > 0


def test_score_mixed_case_user_input():
    project = _make_project(skills=["Python"])
    user_skills = parse_skills("PyThOn")
    score = score_single_project(project, user_skills, **_BEGINNER_DATA_LOW)
    assert score > 0


def test_score_multiple_skills_uppercase():
    project = _make_project(skills=["Python", "HTML"], interest="Web", level="Beginner", time="Low")
    user_skills = parse_skills("PYTHON, HTML")
    score = score_single_project(project, user_skills, "beginner", "web", "low")
    assert score > 0


def test_score_project_with_uppercase_tags():
    """Project tags in ALL CAPS should still match lowercase user skills."""
    project = _make_project(skills=["PYTHON", "HTML"])
    user_skills = parse_skills("python, html")
    score = score_single_project(project, user_skills, **_BEGINNER_DATA_LOW)
    assert score > 0


def test_score_whitespace_in_user_skill():
    project = _make_project(skills=["Python"])
    user_skills = parse_skills(" python ")
    score = score_single_project(project, user_skills, **_BEGINNER_DATA_LOW)
    assert score > 0


# ---------------------------------------------------------------------------
# get_recommendations — end-to-end case insensitivity (Issue #1130 regression)
# ---------------------------------------------------------------------------

def test_recommendations_lowercase_returns_results():
    """Regression for Issue #1130: lowercase skill must not produce zero results."""
    result = get_recommendations("python", "Beginner", "Data", "Low")
    assert len(result["recommendations"]) > 0


def test_recommendations_uppercase_returns_results():
    result = get_recommendations("PYTHON", "Beginner", "Data", "Low")
    assert len(result["recommendations"]) > 0


def test_recommendations_mixed_case_returns_results():
    result = get_recommendations("PyThOn", "Beginner", "Data", "Low")
    assert len(result["recommendations"]) > 0


def test_recommendations_whitespace_returns_results():
    result = get_recommendations(" python ", "Beginner", "Data", "Low")
    assert len(result["recommendations"]) > 0


def test_recommendations_multiple_skills_uppercase():
    result = get_recommendations("PYTHON, HTML", "Beginner", "Web", "Low")
    assert len(result["recommendations"]) > 0


def test_recommendations_case_variants_identical():
    """All case variants must return the same recommendations."""
    ids_lower = [p["id"] for p in get_recommendations("python", "Beginner", "Data", "Low")["recommendations"]]
    ids_upper = [p["id"] for p in get_recommendations("PYTHON", "Beginner", "Data", "Low")["recommendations"]]
    ids_mixed = [p["id"] for p in get_recommendations("PyThOn", "Beginner", "Data", "Low")["recommendations"]]
    ids_space = [p["id"] for p in get_recommendations(" python ", "Beginner", "Data", "Low")["recommendations"]]

    assert ids_upper == ids_lower
    assert ids_mixed == ids_lower
    assert ids_space == ids_lower
