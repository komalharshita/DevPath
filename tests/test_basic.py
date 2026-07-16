import sys
import os
import pytest

# Allow imports from the project root when running tests directly
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from utils.data_loader import load_all_projects, find_project_by_id, clear_cache, validate_projects
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


def test_score_coverage_ratio_exact_values():
    """Verify the coverage-weighted formula produces the correct numeric result."""
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
    assert score == pytest.approx(WEIGHT_LEVEL + WEIGHT_INTEREST + WEIGHT_TIME)  # 2+2+1 = 5


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
    assert len(results) == 0


def test_get_recommendations_result_format():
    """Each returned project must be a dict with at least a title and id."""
    results = get_recommendations("Python", "Beginner", "Data", "Low")
    for project in results:
        assert "id" in project
        assert "title" in project


def test_case_insensitive_recommendations_identical():
    """Lowercase and titlecase skill inputs must produce identical recommendations."""
    results_lower = get_recommendations("python", "Beginner", "Data", "Low")
    results_title = get_recommendations("Python", "Beginner", "Data", "Low")
    assert [p["id"] for p in results_lower] == [p["id"] for p in results_title]


def test_whitespace_stripped_in_skills():
    """Leading/trailing whitespace in the skills string must be ignored."""
    results_clean = get_recommendations("python", "Beginner", "Data", "Low")
    results_spaced = get_recommendations("   python  ", "Beginner", "Data", "Low")
    assert [p["id"] for p in results_clean] == [p["id"] for p in results_spaced]


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


def test_contact_page_renders_send_message_form():
    """Contact page should include the external form handler and required fields."""
    client = get_client()
    response = client.get("/contact")

    assert response.status_code == 200
    html = response.get_data(as_text=True)

    assert 'class="contact-form"' in html
    assert 'action="https://formspree.io/f/your-form-id"' in html
    assert 'method="POST"' in html
    assert 'name="name"' in html
    assert 'name="email"' in html
    assert 'name="message"' in html
    assert "Send Message" in html


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

def test_search_api_no_match():
    """Search should return empty list for nonsense query."""
    client = get_client()
    response = client.get("/api/search?q=nonexistentqueryxyz")
    assert response.status_code == 200

    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) == 0
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
