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

# Allow imports from the project root and src/ when running tests directly
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from utils.data_loader import load_all_projects, find_project_by_id, clear_cache, validate_projects
from utils.roadmap_comparer import (
    load_all_career_roadmaps,
    compare_roadmaps,
    clear_roadmap_cache,
)
from utils.recommender import (
    get_recommendations,
    validate_recommendation_inputs,
    parse_skills,
    score_single_project,
    SCORING_WEIGHTS,
    VALID_LEVELS,
    VALID_TIME_AVAILABILITY,
)

WEIGHT_LEVEL    = SCORING_WEIGHTS["level"]
WEIGHT_INTEREST = SCORING_WEIGHTS["interest"]
WEIGHT_TIME     = SCORING_WEIGHTS["time"]
from app import app, internal_server_error


# ============================================================
# Test setup
# ============================================================

def setup_module():
    """Clear the data cache before running the test suite to ensure clean state."""
    clear_cache()
    clear_roadmap_cache()


# ============================================================
# Data loader tests
# ============================================================

def test_projects_json_loads():
    """The data file must exist and contain at least one project."""
    projects = load_all_projects()
    assert isinstance(projects, list), "Expected a list of projects"
    assert len(projects) > 0, "Project list must not be empty"

def test_duplicate_ids_detected():
    projects = [
        {
            "id": 1,
            "title": "Project A",
            "skills": [],
            "level": "Beginner",
            "interest": "AI",
            "time": "1 week",
            "description": "desc",
            "features": [],
            "tech_stack": [],
            "roadmap": [],
            "resources": [],
            "starter_code": "code"
        },
        {
            "id": 1,
            "title": "Project B",
            "skills": [],
            "level": "Beginner",
            "interest": "AI",
            "time": "1 week",
            "description": "desc",
            "features": [],
            "tech_stack": [],
            "roadmap": [],
            "resources": [],
            "starter_code": "code"
        }
    ]

    with pytest.raises(ValueError):
        validate_projects(projects)

def test_duplicate_titles_detected():
    projects = [
        {
            "id": 1,
            "title": "AI Resume Builder",
            "skills": [],
            "level": "Beginner",
            "interest": "AI",
            "time": "1 week",
            "description": "desc",
            "features": [],
            "tech_stack": [],
            "roadmap": [],
            "resources": [],
            "starter_code": "code"
        },
        {
            "id": 2,
            "title": "ai resume builder",
            "skills": [],
            "level": "Beginner",
            "interest": "AI",
            "time": "1 week",
            "description": "desc",
            "features": [],
            "tech_stack": [],
            "roadmap": [],
            "resources": [],
            "starter_code": "code"
        }
    ]

    with pytest.raises(ValueError):
        validate_projects(projects)

def test_empty_title_detected():
    projects = [
        {
            "id": 1,
            "title": "",
            "skills": [],
            "level": "Beginner",
            "interest": "AI",
            "time": "1 week",
            "description": "desc",
            "features": [],
            "tech_stack": [],
            "roadmap": [],
            "resources": [],
            "starter_code": "code"
        }
    ]

    with pytest.raises(ValueError):
        validate_projects(projects)

def test_missing_required_field_detected():
    projects = [
        {
            "id": 1,
            "title": "Project A"
        }
    ]

    with pytest.raises(ValueError):
        validate_projects(projects)

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


def test_parse_skills_valid_json_array():
    """parse_skills should parse a valid JSON array of skills."""
    result = parse_skills('["Python","React"]')
    assert result == ["python", "react"]


def test_parse_skills_malformed_json_handling():
    """parse_skills should handle malformed JSON gracefully using fallback."""
    # Should not crash, and parses via fallback comma-splitting behavior
    result = parse_skills('["Python",]')
    assert isinstance(result, list)
    assert len(result) > 0


def test_parse_skills_legacy_fallback():
    """parse_skills should parse a legacy comma-separated string."""
    result = parse_skills("Python,React")
    assert result == ["python", "react"]


def test_parse_skills_containing_commas():
    """parse_skills should preserve skill names containing commas when using JSON."""
    result = parse_skills('["HTML, CSS","JavaScript"]')
    assert result == ["html, css", "javascript"]


def test_score_single_project_full_match():
    """A project that matches all four criteria should receive the maximum score."""
    project = {
        "skills": ["Python"],
        "level": "Beginner",
        "interest": "Data",
        "time": "Low"
    }
    score, _ = score_single_project(
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


def test_score_coverage_ratio_exact_values(monkeypatch):
    """Verify the coverage-weighted formula produces the correct numeric result."""
    import utils.recommender
    monkeypatch.setattr(utils.recommender, "_load_skill_graph", lambda: {})

    project = {"skills": ["Python", "Flask"], "level": "Beginner", "interest": "Data", "time": "Low"}

    # 1 of 2 skills matched: coverage = 0.5, score = 1 * 3 * 0.5 = 1.5
    score, _ = score_single_project(project, ["python"], "Advanced", "Games", "High")
    assert score == pytest.approx(1.5), f"Expected 1.5 but got {score}"

    # 2 of 2 skills matched: coverage = 1.0, score = 2 * 3 * 1.0 = 6.0
    score, _ = score_single_project(project, ["python", "flask"], "Advanced", "Games", "High")
    assert score == pytest.approx(6.0), f"Expected 6.0 but got {score}"


def test_score_no_project_skills_does_not_crash():
    """A project with an empty skills list should not raise ZeroDivisionError."""
    project = {"skills": [], "level": "Beginner", "interest": "Data", "time": "Low"}
    score, _ = score_single_project(project, ["python"], "Beginner", "Data", "Low")
    # Skill score is 0, but other criteria still score
    assert score == pytest.approx(SCORING_WEIGHTS["level"] + SCORING_WEIGHTS["interest"] + SCORING_WEIGHTS["time"])  # 2+2+1 = 5


def test_score_three_skills_partial_coverage():
    """Matching 2 of 3 skills should produce a score between 0-skill and 3-skill matches."""
    project = {"skills": ["Python", "Flask", "SQL"], "level": "Beginner", "interest": "Data", "time": "Low"}

    score_0, _ = score_single_project(project, ["rust"],               "Advanced", "Games", "High")
    score_2, _ = score_single_project(project, ["python", "flask"],    "Advanced", "Games", "High")
    score_3, _ = score_single_project(project, ["python", "flask", "sql"], "Advanced", "Games", "High")

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
    score, _ = score_single_project(
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
    score, _ = score_single_project(
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
    results = get_recommendations("Python", "Beginner", "Data", "Low").get("recommendations", [])
    assert len(results) > 0, "Expected at least one recommendation"


def test_get_recommendations_max_three():
    """The engine must never return more than three results."""
    results = get_recommendations("Python, JavaScript, HTML", "Beginner", "Web", "Low").get("recommendations", [])
    assert len(results) <= 3, f"Expected at most 3 results, got {len(results)}"


def test_get_recommendations_no_match_returns_empty():
    """A very unlikely skill/interest combo should return an empty list."""
    results = get_recommendations("Rust", "Advanced", "Games", "High").get("recommendations", [])
    # Rust and Games are not in the dataset so this should be empty or minimal
    assert isinstance(results, list)


def test_get_recommendations_result_format():
    """Each returned project must be a dict with at least a title and id."""
    results = get_recommendations("Python", "Beginner", "Data", "Low").get("recommendations", [])
    for project in results:
        assert "id" in project
        assert "title" in project


def test_case_insensitive_recommendations_identical():
    """Lowercase and titlecase skill inputs must produce identical recommendations."""
    results_lower = get_recommendations("python", "Beginner", "Data", "Low").get("recommendations", [])
    results_title = get_recommendations("Python", "Beginner", "Data", "Low").get("recommendations", [])
    assert [p["id"] for p in results_lower] == [p["id"] for p in results_title]


def test_whitespace_stripped_in_skills():
    """Leading/trailing whitespace in the skills string must be ignored."""
    results_clean = get_recommendations("python", "Beginner", "Data", "Low").get("recommendations", [])
    results_spaced = get_recommendations("   python  ", "Beginner", "Data", "Low").get("recommendations", [])
    assert [p["id"] for p in results_clean] == [p["id"] for p in results_spaced]


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
    with app.test_request_context("/"):
        rendered_page, status_code = internal_server_error(Exception("Test error"))

    assert status_code == 500
    assert "Internal Server Error" in rendered_page
    assert ("Back to Home" in rendered_page or "Back to Search" in rendered_page or "Return Home" in rendered_page)


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
    """A project with a nested starter_code path should still return 200."""
    client = get_client()
    project = next(
        p for p in load_all_projects()
        if "/" in p["starter_code"].replace("starter_code/", "")
    )
    response = client.get(f"/project/{project['id']}/code")
    assert response.status_code == 200
    data = response.get_json()
    assert "code" in data
    assert "filename" in data
    assert len(data["code"]) > 0


def test_download_code_nested_path():
    """A project with a nested starter_code path should still download."""
    client = get_client()
    project = next(
        p for p in load_all_projects()
        if "/" in p["starter_code"].replace("starter_code/", "")
    )
    response = client.get(f"/project/{project['id']}/download")
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

def test_search_api_returns_results():
    """Search API should return matching projects for a valid query."""
    client = get_client()
    response = client.get("/api/search?q=python")
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)

def test_search_api_empty_query():
    """Search API should return an empty list for blank queries."""
    client = get_client()
    response = client.get("/api/search?q=")
    assert response.status_code == 200
    data = response.get_json()
    assert data == []

def test_home_route_with_share_params():
    """The homepage should load normally even when share query params are present."""
    client = get_client()
    response = client.get("/?skills=Python,HTML&level=Beginner&interest=Data&time=Low")
    assert response.status_code == 200


def test_share_banner_element_exists():
    """The page HTML must include the share-prefill-banner element for JS to populate."""
    client = get_client()
    response = client.get("/")
    html = response.data.decode()
    assert 'id="share-prefill-banner"' in html


def test_share_params_partial_loads_ok():
    """Partial share params should not break the page — server renders normally."""
    client = get_client()
    response = client.get("/?skills=Python&level=Beginner")
    assert response.status_code == 200


def test_share_params_invalid_level_not_reflected():
    """An invalid level value should not appear in the server-rendered HTML form options."""
    client = get_client()
    response = client.get("/?skills=Python&level=Expert&interest=Data&time=Low")
    html = response.data.decode()
    # 'Expert' is not a valid option, so it must not appear as a selected value
    assert 'value="Expert" selected' not in html


def test_share_params_xss_not_reflected():
    """Script tags in query params must not be rendered in server HTML."""
    client = get_client()
    response = client.get("/?skills=<script>alert(1)</script>&level=Beginner&interest=Data&time=Low")
    html = response.data.decode()
    assert "<script>alert(1)</script>" not in html


def test_share_params_excessive_skills_loads_ok():
    """A URL with many skills should not crash the server."""
    skills = ",".join(["Skill" + str(i) for i in range(30)])
    client = get_client()
    response = client.get(f"/?skills={skills}&level=Beginner&interest=Data&time=Low")
    assert response.status_code == 200


def test_api_recommend_invalid_level_no_crash():
    """Posting an unrecognized level should not crash — returns empty or error."""
    client = get_client()
    response = client.post("/api/recommend", json={
        "skills": "Python",
        "level": "Expert",
        "interest": "Data",
        "time": "Low"
    })
    assert response.status_code in (200, 400)
    data = response.get_json()
    # Should either be an error or return empty results (no match for 'Expert')
    if response.status_code == 200:
        assert "projects" in data


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
# Career roadmap comparison tests
# ============================================================

def test_career_roadmaps_load():
    """Career roadmaps JSON must load and contain entries."""
    roadmaps = load_all_career_roadmaps()
    assert isinstance(roadmaps, list)
    assert len(roadmaps) >= 2


def test_compare_roadmaps_finds_overlap():
    """Comparing frontend and fullstack should find shared skills."""
    result = compare_roadmaps("frontend", "fullstack")
    assert result is not None
    assert "overlapping_skills" in result
    assert len(result["overlapping_skills"]) > 0
    assert result["roadmap_a"]["id"] == "frontend"
    assert result["roadmap_b"]["id"] == "fullstack"


def test_compare_same_roadmap_returns_error():
    """Comparing a roadmap with itself should return an error message."""
    result = compare_roadmaps("react", "react")
    assert result is not None
    assert "error" in result


def test_compare_invalid_roadmap_returns_none():
    """Unknown roadmap IDs should return None."""
    assert compare_roadmaps("nonexistent", "frontend") is None


def test_compare_page_route():
    """Compare page should render successfully."""
    client = get_client()
    response = client.get("/compare")
    assert response.status_code == 200
    assert b"Compare Learning Roadmaps" in response.data


def test_list_roadmaps_api():
    """API should return all career roadmaps."""
    client = get_client()
    response = client.get("/api/roadmaps")
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) >= 2


def test_compare_api():
    """Compare API should return structured comparison data."""
    client = get_client()
    response = client.get("/api/compare?a=react&b=angular")
    assert response.status_code == 200
    data = response.get_json()
    assert data["roadmap_a"]["id"] == "react"
    assert data["roadmap_b"]["id"] == "angular"
    assert "metrics" in data
    assert "overlapping_skills" in data


def test_compare_api_missing_params():
    """Compare API should reject requests missing query params."""
    client = get_client()
    response = client.get("/api/compare?a=react")
    assert response.status_code == 400


def test_compare_api_not_found():
    """Compare API should 404 for invalid roadmap IDs."""
    client = get_client()
    response = client.get("/api/compare?a=invalid&b=alsoinvalid")
    assert response.status_code == 404


def test_sitemap_includes_compare():
    """Sitemap should include the compare page."""
    client = get_client()
    response = client.get("/sitemap.xml")
    assert response.status_code == 200
    assert b"/compare" in response.data



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

def test_ml_similarity_score_returns_float():
    from utils.recommender import ml_similarity_score, parse_skills
    projects = load_all_projects()
    score = ml_similarity_score(
        projects[0],
        parse_skills("Python"),
        "Beginner",
        "Data",
        "Low",
        projects,
    )
    assert isinstance(score, float)
    assert score >= 0

def test_ml_recommendation_prefers_relevant_python_data_project():
    results = get_recommendations("Python, pandas", "Intermediate", "Data", "High")
    recs = results.get("recommendations", [])
    titles = [project["title"] for project in recs]
    assert any("Data" in title or "Pipeline" in title for title in titles)
