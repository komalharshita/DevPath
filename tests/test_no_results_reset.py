# tests/test_no_results_reset.py
# Tests for bug #730 — "No Projects Found" state must fully clear when
# the user submits a new search after a zero-result query.
#
# What is tested
# --------------
# 1. The API correctly returns an empty project list for no-match inputs.
# 2. The API correctly returns projects for match inputs.
# 3. Successive API calls behave independently — a prior empty result does
#    not pollute the next successful result (state lives only in the
#    response, not the server).
# 4. The empty-state message field is present in API responses that have
#    no matches, so the JS can populate emptyMessageEl safely.
# 5. The results section HTML landmark and its three sub-states
#    (loading, empty, grid) all exist in the page so the JS selectors
#    in setLoadingState / renderResults are guaranteed to resolve.
# 6. script.js is served and contains both fixed functions.
#
# Run with:  python -m pytest tests/test_no_results_reset.py -v

import sys
import os

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app import app


# ---------------------------------------------------------------------------
# Fixture
# ---------------------------------------------------------------------------

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


# ---------------------------------------------------------------------------
# Helper payloads
# ---------------------------------------------------------------------------

NO_MATCH_PAYLOAD = {
    "skills": "Python",
    "level": "Advanced",
    "interest": "Machine Learning/AI",
    "time": "Low"
}

MATCH_PAYLOAD = {
    "skills": "Python",
    "level": "Beginner",
    "interest": "Data",
    "time": "Low"
}


# ---------------------------------------------------------------------------
# API state independence — the core of the bug
# ---------------------------------------------------------------------------

def test_no_match_returns_empty_list(client):
    """A blocked interest must return an empty projects list."""
    response = client.post("/api/recommend", json=NO_MATCH_PAYLOAD)
    assert response.status_code == 200
    data = response.get_json()
    assert data["projects"] == []


def test_no_match_returns_message_field(client):
    """Empty result must include a 'message' key for emptyMessageEl."""
    response = client.post("/api/recommend", json=NO_MATCH_PAYLOAD)
    data = response.get_json()
    assert "message" in data, (
        "API must return a 'message' field when projects is empty "
        "so the JS can populate emptyMessageEl without a null-ref error"
    )
    assert isinstance(data["message"], str)
    assert len(data["message"]) > 0


def test_match_after_no_match_returns_projects(client):
    """After a zero-result query, a valid query must return projects normally."""
    # First call — no match (simulates the bug scenario step 2)
    r1 = client.post("/api/recommend", json=NO_MATCH_PAYLOAD)
    assert r1.get_json()["projects"] == []

    # Second call — valid match (simulates step 3-4)
    r2 = client.post("/api/recommend", json=MATCH_PAYLOAD)
    data = r2.get_json()
    assert r2.status_code == 200
    assert len(data["projects"]) > 0, (
        "Valid query after a no-match query must still return projects — "
        "the server must not carry state between requests"
    )


def test_match_after_no_match_has_no_message(client):
    """A successful result must NOT include a blocking 'message' field
    (or if it does, projects must be non-empty — they must not both be set
    in a way that would cause the empty-state branch to render)."""
    client.post("/api/recommend", json=NO_MATCH_PAYLOAD)
    r2 = client.post("/api/recommend", json=MATCH_PAYLOAD)
    data = r2.get_json()
    # Either no message, or projects are present (non-empty result wins)
    if "message" in data:
        assert len(data["projects"]) > 0, (
            "If 'message' is present alongside projects, projects must be "
            "non-empty so renderResults takes the success branch"
        )


def test_repeated_no_match_queries_are_consistent(client):
    """Multiple consecutive no-match queries must all return empty lists."""
    for _ in range(3):
        r = client.post("/api/recommend", json=NO_MATCH_PAYLOAD)
        assert r.get_json()["projects"] == []


def test_repeated_match_queries_are_consistent(client):
    """Multiple consecutive match queries must all return the same projects."""
    results = []
    for _ in range(3):
        r = client.post("/api/recommend", json=MATCH_PAYLOAD)
        results.append([p["id"] for p in r.get_json()["projects"]])
    assert results[0] == results[1] == results[2], (
        "Recommendation results must be deterministic across calls"
    )


def test_alternating_no_match_and_match(client):
    """Alternating no-match / match calls must each return the correct state."""
    for i in range(4):
        if i % 2 == 0:
            r = client.post("/api/recommend", json=NO_MATCH_PAYLOAD)
            assert r.get_json()["projects"] == [], f"Iteration {i}: expected empty"
        else:
            r = client.post("/api/recommend", json=MATCH_PAYLOAD)
            assert len(r.get_json()["projects"]) > 0, f"Iteration {i}: expected results"


# ---------------------------------------------------------------------------
# HTML landmark presence — JS selectors must resolve
# ---------------------------------------------------------------------------

def test_results_section_present(client):
    """#results-section must exist — setLoadingState targets it."""
    r = client.get("/")
    assert b'id="results-section"' in r.data


def test_results_loading_present(client):
    """#results-loading must exist — setLoadingState shows/hides it."""
    r = client.get("/")
    assert b'id="results-loading"' in r.data


def test_results_empty_present(client):
    """#results-empty must exist — renderResults shows it on zero results."""
    r = client.get("/")
    assert b'id="results-empty"' in r.data


def test_results_grid_present(client):
    """#results-grid must exist — renderResults populates it."""
    r = client.get("/")
    assert b'id="results-grid"' in r.data


def test_empty_message_element_present(client):
    """#empty-message must exist — renderResults sets its textContent."""
    r = client.get("/")
    assert b'id="empty-message"' in r.data, (
        "#empty-message element is missing; renderResults will throw a "
        "null-reference error when trying to set emptyMessageEl.textContent"
    )


def test_results_section_initially_hidden(client):
    """results-section must start hidden (display:none inline style)."""
    r = client.get("/")
    # The template sets style="display:none;" on the section
    assert b'id="results-section"' in r.data
    # Check the inline style is present in the same element
    html = r.data.decode("utf-8")
    idx = html.find('id="results-section"')
    # Grab a window of chars around the element opening tag
    snippet = html[max(0, idx - 10): idx + 120]
    assert "display:none" in snippet or "display: none" in snippet, (
        "results-section must have display:none so it is hidden before the "
        "first search; the JS reveals it in setLoadingState"
    )


# ---------------------------------------------------------------------------
# script.js contains the fixed functions
# ---------------------------------------------------------------------------

def test_script_js_served(client):
    r = client.get("/static/script.js")
    assert r.status_code == 200


def test_script_js_clears_results_grid_on_loading(client):
    """setLoadingState must clear resultsGrid.innerHTML when isLoading=true."""
    r = client.get("/static/script.js")
    js = r.data.decode("utf-8")
    # The fix sets resultsGrid.innerHTML = "" inside the isLoading branch
    assert 'resultsGrid.innerHTML = ""' in js or "resultsGrid.innerHTML=''" in js, (
        "setLoadingState must set resultsGrid.innerHTML to '' when isLoading "
        "is true so stale cards from a previous search are removed immediately"
    )


def test_script_js_hides_empty_state_on_loading(client):
    """setLoadingState must hide resultsEmptyEl when starting a new search."""
    r = client.get("/static/script.js")
    js = r.data.decode("utf-8")
    assert 'resultsEmptyEl.style.display = "none"' in js, (
        "setLoadingState must hide resultsEmptyEl so the No Projects Found "
        "card does not remain visible during a new search"
    )


def test_script_js_render_results_resets_grid_display(client):
    """renderResults must reset grid display before populating it."""
    r = client.get("/static/script.js")
    js = r.data.decode("utf-8")
    assert 'resultsGrid.innerHTML = ""' in js, (
        "renderResults must clear innerHTML before appending new cards"
    )


def test_script_js_render_results_guards_empty_message_el(client):
    """renderResults must guard emptyMessageEl with a null check."""
    r = client.get("/static/script.js")
    js = r.data.decode("utf-8")
    # The fix wraps emptyMessageEl.textContent assignment in an if check
    assert "if (emptyMessageEl)" in js, (
        "renderResults must guard emptyMessageEl against null to prevent "
        "TypeError when the element is unexpectedly absent"
    )
