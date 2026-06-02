# tests/test_basic.py
# Basic tests for core DevPath functionality.
#
# Run with:   python -m pytest tests/
# Or:         python tests/test_basic.py
#
# These tests check that:
#   - The projects dataset loads without errors
#   - The recommendation engine returns sensible results
#   - Input validation catches bad data
#   - All main HTTP routes return the expected status codes

import sys
import os

import pytest

# Allow imports from the project root when running tests directly
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils.data_loader import load_all_projects, find_project_by_id, clear_cache
from utils.recommender import (
    get_recommendations,
    validate_recommendation_inputs,
    parse_skills,
    score_single_project,
    WEIGHT_LEVEL,
    WEIGHT_INTEREST,
    WEIGHT_TIME,
)
from app import app, internal_server_error


# ============================================================
# Test setup
# ============================================================

def setup_module():
    """Clear the data cache before running the test suite to ensure clean state."""
    clear_cache()


# ============================================================
# Data loader tests
# ============================================================

def test_projects_json_loads():
    """The data file must exist and contain at least one project."""
    projects = load_all_projects()
    assert isinstance(projects, list), "Expected a list of projects"
    assert len(projects) > 0, "Project list must not be empty"


def test_each_project_has_required_fields():
    """Every project must have the fields the UI depends on."""
    required = ["id", "title", "skills", "level", "interest", "time",
                "description", "features", "tech_stack", "roadmap",
                "resources", "starter_code"]
    for project in load_all_projects():
        for field in required:
            assert field in project, f"Project '{project.get('title')}' is missing field: {field}"


def test_find_project_by_id_found():
    """find_project_by_id should return the correct project when the ID exists."""
    project = find_project_by_id(1)
    assert project is not None, "Expected project with id=1 to exist"
    assert project["id"] == 1


def test_find_project_by_id_missing():
    """find_project_by_id should return None for an ID that does not exist."""
    result = find_project_by_id(99999)
    assert result is None, "Expected None for a non-existent project ID"


# ============================================================
# Recommender utility tests
# ============================================================

def test_parse_skills_basic():
    """parse_skills should split on commas and lowercase each entry."""
    result = parse_skills("Python, HTML, CSS")
    assert result == ["python", "html", "css"]


def test_parse_skills_empty_string():
    """parse_skills should return an empty list for blank input."""
    assert parse_skills("") == []
    assert parse_skills("   ") == []


def test_parse_skills_single_entry():
    """parse_skills should handle a single skill with no commas."""
    assert parse_skills("JavaScript") == ["javascript"]


def test_score_single_project_full_match():
    """A project that matches all four criteria should receive the maximum score."""
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
    # 1 skill match (3) + level (2) + interest (2) + time (1) = 8
    assert score == pytest.approx(8), f"Expected 8 but got {score}"
# --------------
def test_score_single_project_partial_skill_coverage():
    """Matching 1 of 2 required skills should score less than matching both."""
    project = {
        "skills": ["Python", "Flask"],
        "level": "Beginner",
        "interest": "Data",
        "time": "Low"
    }
    # User knows only Python (1 of 2)
    score_partial = score_single_project(
        project,
        user_skills=["python"],
        level="Beginner",
        interest="Data",
        time_availability="Low"
    )
    # User knows both Python and Flask (2 of 2)
    score_full = score_single_project(
        project,
        user_skills=["python", "flask"],
        level="Beginner",
        interest="Data",
        time_availability="Low"
    )
    assert score_partial < score_full, (
        f"Partial match ({score_partial}) should score less than full match ({score_full})"
    )


def test_score_coverage_ratio_exact_values():
    """Verify the coverage-weighted formula produces the correct numeric result."""
    project = {"skills": ["Python", "Flask"], "level": "Beginner", "interest": "Data", "time": "Low"}

    # 1 of 2 skills matched: coverage = 0.5, score = 1 * 3 * 0.5 = 1.5
    score = score_single_project(project, ["python"], "Advanced", "Games", "High")
    assert score == pytest.approx(1.5), f"Expected 1.5 but got {score}"

    # 2 of 2 skills matched: coverage = 1.0, score = 2 * 3 * 1.0 = 6.0
    score = score_single_project(project, ["python", "flask"], "Advanced", "Games", "High")
    assert score == pytest.approx(6.0), f"Expected 6.0 but got {score}"


def test_score_no_project_skills_does_not_crash():
    """A project with an empty skills list should not raise ZeroDivisionError."""
    project = {"skills": [], "level": "Beginner", "interest": "Data", "time": "Low"}
    score = score_single_project(project, ["python"], "Beginner", "Data", "Low")
    # Skill score is 0, but other criteria still score
    assert score == pytest.approx(WEIGHT_LEVEL + WEIGHT_INTEREST + WEIGHT_TIME)  # 2+2+1 = 5


def test_score_three_skills_partial_coverage():
    """Matching 2 of 3 skills should produce a score between 0-skill and 3-skill matches."""
    project = {"skills": ["Python", "Flask", "SQL"], "level": "Beginner", "interest": "Data", "time": "Low"}

    score_0 = score_single_project(project, ["rust"],               "Advanced", "Games", "High")
    score_2 = score_single_project(project, ["python", "flask"],    "Advanced", "Games", "High")
    score_3 = score_single_project(project, ["python", "flask", "sql"], "Advanced", "Games", "High")

    assert score_0 == pytest.approx(0)
    assert score_0 < score_2 < score_3, (
        f"Expected 0 < {score_2} < {score_3}"
    )
# --------------


def test_score_single_project_no_match():
    """A project with no overlap should score zero."""
    project = {
        "skills": ["Rust"],
        "level": "Advanced",
        "interest": "Games",
        "time": "High"
    }
    score = score_single_project(
        project,
        user_skills=["python"],
        level="Beginner",
        interest="Data",
        time_availability="Low"
    )
    assert score == pytest.approx(0), f"Expected 0 but got {score}"


def test_score_single_project_alias_matching():
    """Project skills should be alias-resolved so 'JS' in a project matches 'javascript' from the user."""
    project = {
        "skills": ["JS"],
        "level": "Beginner",
        "interest": "Web",
        "time": "Low"
    }
    score = score_single_project(
        project,
        user_skills=["javascript"],
        level="Beginner",
        interest="Web",
        time_availability="Low"
    )
    # 1 skill match (3) + level (2) + interest (2) + time (1) = 8
    assert score == 8, f"Expected 8 but got {score}"


def test_get_recommendations_returns_results():
    """Python + Beginner + Data + Low should always return at least one result."""
    results = get_recommendations("Python", "Beginner", "Data", "Low")
    assert len(results) > 0, "Expected at least one recommendation"


def test_get_recommendations_max_three():
    """The engine must never return more than three results."""
    results = get_recommendations("Python, JavaScript, HTML", "Beginner", "Web", "Low")
    assert len(results) <= 3, f"Expected at most 3 results, got {len(results)}"


def test_get_recommendations_no_match_returns_empty():
    """A very unlikely skill/interest combo should return an empty list."""
    results = get_recommendations("Rust", "Advanced", "Games", "High")
    # Rust and Games are not in the dataset so this should be empty or minimal
    assert isinstance(results, list)


def test_get_recommendations_result_format():
    """Each returned project must be a dict with at least a title and id."""
    results = get_recommendations("Python", "Beginner", "Data", "Low")
    for project in results:
        assert "id" in project
        assert "title" in project


# ============================================================
# Input validation tests
# ============================================================

def test_validate_all_valid():
    """No errors should be returned when all fields are provided."""
    errors = validate_recommendation_inputs("Python", "Beginner", "Web", "Low")
    assert errors == [], f"Unexpected errors: {errors}"


def test_validate_missing_skills():
    """An empty skills field must produce an error."""
    errors = validate_recommendation_inputs("", "Beginner", "Web", "Low")
    assert len(errors) > 0


def test_validate_missing_level():
    errors = validate_recommendation_inputs("Python", "", "Web", "Low")
    assert len(errors) > 0


def test_validate_missing_interest():
    errors = validate_recommendation_inputs("Python", "Beginner", "", "Low")
    assert len(errors) > 0


def test_validate_missing_time():
    errors = validate_recommendation_inputs("Python", "Beginner", "Web", "")
    assert len(errors) > 0


def test_validate_all_missing():
    """All four fields missing should produce four errors."""
    errors = validate_recommendation_inputs("", "", "", "")
    assert len(errors) == 4


# ============================================================
# HTTP route tests (using Flask test client)
# ============================================================

def get_client():
    """Return a Flask test client with testing mode enabled."""
    app.config["TESTING"] = True
    return app.test_client()


def test_home_route():
    client = get_client()
    response = client.get("/")
    assert response.status_code == 200

def test_security_headers_present():
    """Security headers should be included in all responses."""
    client = get_client()
    response = client.get("/")

    assert response.headers["X-Frame-Options"] == "DENY"
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert (
        response.headers["Referrer-Policy"]
        == "strict-origin-when-cross-origin"
    )
    assert (
        response.headers["Permissions-Policy"]
        == "geolocation=(), microphone=(), camera=()"
    )


def test_recommend_api_valid():
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
    assert len(data["projects"]) > 0


def test_recommend_api_interest_not_available():
    """The API should return no projects for blocked interest categories."""
    client = get_client()
    response = client.post("/api/recommend", json={
        "skills": "Python, JavaScript",
        "level": "Beginner",
        "interest": "Machine Learning/AI",
        "time": "Low"
    })
    assert response.status_code == 200
    data = response.get_json()
    assert data["projects"] == []
    assert "message" in data
    assert "no projects are currently available" in data["message"].lower()


def test_recommend_api_missing_field():
    """The API should return 400 when a required field is missing."""
    client = get_client()
    response = client.post("/api/recommend", json={
        "skills": "",
        "level": "Beginner",
        "interest": "Data",
        "time": "Low"
    })
    assert response.status_code in (400, 415)
    assert "error" in response.get_json()


def test_recommend_api_null_field():
    """The API should return 400 when a field is explicitly set to null."""
    client = get_client()
    response = client.post("/api/recommend", json={
        "skills": None,
        "level": "Beginner",
        "interest": "Web",
        "time": "Low"
    })
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data


def test_recommend_api_non_string_field():
    """The API should return 400 when a field is a non-string type (e.g. a list)."""
    client = get_client()
    response = client.post("/api/recommend", json={
        "skills": ["Python", "HTML"],
        "level": "Beginner",
        "interest": "Web",
        "time": "Low"
    })
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data


def test_recommend_api_empty_body():
    """The API should return 400 when the body is not valid JSON."""
    client = get_client()
    response = client.post("/api/recommend",
                           data="not json",
                           content_type="text/plain")
    assert response.status_code in (400, 415)


def test_project_detail_found():
    client = get_client()
    response = client.get("/project/1")
    assert response.status_code == 200


def test_project_detail_not_found():
    client = get_client()
    response = client.get("/project/99999")
    assert response.status_code == 404


def test_internal_server_error_page():
    """The 500 handler should render the friendly internal error template."""
    with app.app_context():
        rendered_page, status_code = internal_server_error(Exception("Test error"))

    assert status_code == 500
    assert "Internal Server Error" in rendered_page
    assert "Back to Home" in rendered_page


def test_view_code_found():
    client = get_client()
    response = client.get("/project/1/code")
    assert response.status_code == 200
    data = response.get_json()
    assert "code" in data
    assert "filename" in data
    assert len(data["code"]) > 0


def test_download_code_found():
    client = get_client()
    response = client.get("/project/1/download")
    assert response.status_code == 200


def test_view_code_nested_path():
    """Project 9 has a nested starter_code path; /code should still return 200."""
    client = get_client()
    response = client.get("/project/9/code")
    assert response.status_code == 200
    data = response.get_json()
    assert "code" in data
    assert "filename" in data
    assert len(data["code"]) > 0


def test_download_code_nested_path():
    """Project 9 has a nested starter_code path; /download should still return 200."""
    client = get_client()
    response = client.get("/project/9/download")
    assert response.status_code == 200


def test_resolve_starter_file_path_traversal():
    """resolve_starter_file must return None for path traversal attempts."""
    from utils.file_server import resolve_starter_file
    malicious = {"starter_code": "starter_code/../../routes/main_routes.py"}
    assert resolve_starter_file(malicious) is None
    
def test_health_check():
    client = get_client()
    response = client.get("/health")
    assert response.status_code == 200
    data = response.get_json()
    assert "status" in data
    assert "version" in data
    assert data["status"] == "ok"


from utils.recommender import SCORING_WEIGHTS

def test_scoring_weights_has_all_keys():
    """Verify SCORING_WEIGHTS contains exactly the four expected keys."""
    expected_keys = {"skill", "level", "interest", "time"}
    assert set(SCORING_WEIGHTS.keys()) == expected_keys


# ============================================================
# Sitemap and robots.txt tests
# ============================================================

def test_sitemap_returns_200():
    """The /sitemap.xml route must return HTTP 200."""
    client = get_client()
    response = client.get("/sitemap.xml")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"


def test_sitemap_content_type():
    """The /sitemap.xml route must return XML content type."""
    client = get_client()
    response = client.get("/sitemap.xml")
    assert "application/xml" in response.content_type, (
        f"Expected application/xml, got {response.content_type}"
    )


def test_sitemap_contains_homepage():
    """The sitemap must include the homepage URL."""
    client = get_client()
    response = client.get("/sitemap.xml")
    assert b"<loc>" in response.data, "Expected <loc> tags in sitemap"
    assert b"</urlset>" in response.data, "Expected closing </urlset> tag"


def test_sitemap_contains_all_project_ids():
    """The sitemap must include a URL for every project in the dataset."""
    client = get_client()
    response = client.get("/sitemap.xml")
    xml = response.data.decode("utf-8")

    projects = load_all_projects()
    for project in projects:
        expected = f"/project/{project['id']}"
        assert expected in xml, (
            f"Sitemap missing URL for project id={project['id']}"
        )


def test_robots_txt_returns_200():
    """The /robots.txt route must return HTTP 200."""
    client = get_client()
    response = client.get("/robots.txt")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"


def test_robots_txt_references_sitemap():
    """robots.txt must contain the Sitemap directive."""
    client = get_client()
    response = client.get("/robots.txt")
    assert b"Sitemap:" in response.data, "robots.txt must contain a Sitemap: directive"
    assert b"sitemap.xml" in response.data, "robots.txt must reference sitemap.xml"

def test_project_links_have_noopener():
    client = app.test_client()

    response = client.get("/project/1")

    assert response.status_code == 200
    assert b'target="_blank"' in response.data
    assert b'rel="noopener noreferrer"' in response.data



# ============================================================
# Run tests directly (no pytest required)
# ============================================================

if __name__ == "__main__":
    test_functions = [v for k, v in list(globals().items()) if k.startswith("test_")]
    passed = 0
    failed = 0

    for fn in test_functions:
        try:
            fn()
            print(f"  PASS  {fn.__name__}")
            passed += 1
        except Exception as exc:
            print(f"  FAIL  {fn.__name__}: {exc}")
            failed += 1

    print(f"\n{passed} passed, {failed} failed out of {passed + failed} tests")
    if failed > 0:
        sys.exit(1)
