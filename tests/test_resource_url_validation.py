# tests/test_resource_url_validation.py
# Tests for bug #781 — learning resource URLs must be validated and
# served as structured objects so broken links can be handled gracefully.
#
# Run with:  python -m pytest tests/test_resource_url_validation.py -v

import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils.url_validator import is_valid_url, parse_resource, validate_resource, validate_resources
from utils.data_loader import load_all_projects, clear_cache
from app import app


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


@pytest.fixture(autouse=True)
def reset_cache():
    clear_cache()
    yield
    clear_cache()


# ---------------------------------------------------------------------------
# is_valid_url
# ---------------------------------------------------------------------------

def test_valid_https_url():
    assert is_valid_url("https://docs.python.org") is True

def test_valid_http_url():
    assert is_valid_url("http://example.com") is True

def test_valid_url_with_path():
    assert is_valid_url("https://docs.python.org/3/library/csv.html") is True

def test_valid_url_with_query():
    assert is_valid_url("https://example.com/search?q=python") is True

def test_valid_url_with_fragment():
    assert is_valid_url("https://example.com/page#section") is True

def test_valid_url_with_port():
    assert is_valid_url("https://localhost:5000/api") is True

def test_invalid_bare_domain():
    assert is_valid_url("example.com") is False

def test_invalid_ftp_scheme():
    assert is_valid_url("ftp://example.com") is False

def test_invalid_mailto():
    assert is_valid_url("mailto:test@example.com") is False

def test_invalid_empty_string():
    assert is_valid_url("") is False

def test_invalid_none():
    assert is_valid_url(None) is False

def test_invalid_plain_text():
    assert is_valid_url("not a url at all") is False

def test_invalid_missing_scheme():
    assert is_valid_url("//example.com/path") is False


# ---------------------------------------------------------------------------
# parse_resource
# ---------------------------------------------------------------------------

def test_parse_label_and_url():
    result = parse_resource("Python official docs: https://docs.python.org")
    assert result["label"] == "Python official docs"
    assert result["url"] == "https://docs.python.org"

def test_parse_url_only():
    result = parse_resource("https://realpython.com")
    assert result["label"] == "https://realpython.com"
    assert result["url"] == "https://realpython.com"

def test_parse_label_with_https_url_and_path():
    result = parse_resource("CSV module guide: https://docs.python.org/3/library/csv.html")
    assert result["label"] == "CSV module guide"
    assert result["url"] == "https://docs.python.org/3/library/csv.html"

def test_parse_does_not_split_on_url_colon():
    """Colons inside the URL (e.g. https://) must not split the label."""
    result = parse_resource("MDN Fetch API: https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API")
    assert result["label"] == "MDN Fetch API"
    assert "developer.mozilla.org" in result["url"]

def test_parse_empty_string():
    result = parse_resource("")
    assert result["label"] == ""
    assert result["url"] == ""

def test_parse_none():
    result = parse_resource(None)
    assert result["label"] == ""
    assert result["url"] == ""

def test_parse_strips_whitespace():
    result = parse_resource("  Label : https://example.com  ")
    assert result["url"] == "https://example.com"


# ---------------------------------------------------------------------------
# validate_resource
# ---------------------------------------------------------------------------

def test_validate_resource_valid():
    result = validate_resource("Python docs: https://docs.python.org")
    assert result["valid"] is True
    assert result["label"] == "Python docs"
    assert result["url"] == "https://docs.python.org"

def test_validate_resource_invalid_url():
    result = validate_resource("Broken link: not-a-url")
    assert result["valid"] is False

def test_validate_resource_empty():
    result = validate_resource("")
    assert result["valid"] is False

def test_validate_resource_has_all_keys():
    result = validate_resource("Label: https://example.com")
    assert "label" in result
    assert "url" in result
    assert "valid" in result


# ---------------------------------------------------------------------------
# validate_resources (list)
# ---------------------------------------------------------------------------

def test_validate_resources_all_valid():
    raw = [
        "Python docs: https://docs.python.org",
        "MDN: https://developer.mozilla.org",
    ]
    results = validate_resources(raw)
    assert len(results) == 2
    assert all(r["valid"] for r in results)

def test_validate_resources_mixed():
    raw = [
        "Good link: https://docs.python.org",
        "Bad link: not-a-url",
    ]
    results = validate_resources(raw)
    assert results[0]["valid"] is True
    assert results[1]["valid"] is False

def test_validate_resources_empty_list():
    assert validate_resources([]) == []

def test_validate_resources_not_a_list():
    assert validate_resources(None) == []


# ---------------------------------------------------------------------------
# All resources in projects.json must have valid URL format
# ---------------------------------------------------------------------------

def test_all_project_resources_have_valid_urls():
    """Every resource URL in projects.json must pass format validation."""
    from utils.url_validator import parse_resource, is_valid_url
    projects = load_all_projects()
    broken = []
    for project in projects:
        for raw in project.get("resources", []):
            parsed = parse_resource(raw)
            url = parsed.get("url", "")
            if url and not is_valid_url(url):
                broken.append((project["id"], project["title"], url))

    assert broken == [], (
        "Malformed resource URLs found in projects.json:\n" +
        "\n".join(f"  project id={pid} '{title}': {url}" for pid, title, url in broken)
    )

def test_all_projects_have_at_least_one_resource():
    """Every project must have at least one learning resource."""
    projects = load_all_projects()
    missing = [p for p in projects if not p.get("resources")]
    assert missing == [], (
        "Projects with no resources: " +
        ", ".join(str(p["id"]) for p in missing)
    )

def test_all_resource_strings_are_non_empty():
    """No resource entry should be an empty string."""
    projects = load_all_projects()
    for project in projects:
        for raw in project.get("resources", []):
            assert raw.strip(), (
                f"Empty resource string in project id={project['id']}"
            )


# ---------------------------------------------------------------------------
# /api/project/<id>/resources route
# ---------------------------------------------------------------------------

def test_resources_route_returns_200(client):
    response = client.get("/api/project/1/resources")
    assert response.status_code == 200

def test_resources_route_returns_json(client):
    response = client.get("/api/project/1/resources")
    data = response.get_json()
    assert data is not None

def test_resources_route_has_project_id(client):
    data = client.get("/api/project/1/resources").get_json()
    assert "project_id" in data
    assert data["project_id"] == 1

def test_resources_route_has_resources_list(client):
    data = client.get("/api/project/1/resources").get_json()
    assert "resources" in data
    assert isinstance(data["resources"], list)

def test_resources_route_each_item_has_label(client):
    data = client.get("/api/project/1/resources").get_json()
    for item in data["resources"]:
        assert "label" in item

def test_resources_route_each_item_has_url(client):
    data = client.get("/api/project/1/resources").get_json()
    for item in data["resources"]:
        assert "url" in item

def test_resources_route_each_item_has_valid_flag(client):
    data = client.get("/api/project/1/resources").get_json()
    for item in data["resources"]:
        assert "valid" in item
        assert isinstance(item["valid"], bool)

def test_resources_route_project_1_all_valid(client):
    """Project 1 resources in the dataset must all pass URL validation."""
    data = client.get("/api/project/1/resources").get_json()
    invalid = [r for r in data["resources"] if not r["valid"]]
    assert invalid == [], f"Invalid resources in project 1: {invalid}"

def test_resources_route_invalid_project_returns_404(client):
    response = client.get("/api/project/99999/resources")
    assert response.status_code == 404
    assert "error" in response.get_json()

def test_resources_route_security_headers(client):
    response = client.get("/api/project/1/resources")
    assert response.headers.get("X-Frame-Options") == "DENY"
    assert response.headers.get("X-Content-Type-Options") == "nosniff"
