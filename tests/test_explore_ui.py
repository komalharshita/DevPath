"""Tests for the interactive Explore page UI enhancements."""


def test_quick_view_modal_present(client):
    """The quick-view modal dialog must be present in explore.html."""
    response = client.get("/explore")
    assert response.status_code == 200
    assert b'id="project-quick-view-modal"' in response.data
    assert b'id="modal-project-title"' in response.data
    assert b'id="modal-project-features"' in response.data
    assert b'id="modal-project-roadmap"' in response.data


def test_tech_chips_bar_present(client):
    """Popular tech stack filter chips bar must be present."""
    response = client.get("/explore")
    assert response.status_code == 200
    assert b'class="tech-chips-bar-wrapper"' in response.data
    assert b'data-skill-chip=""' in response.data


def test_card_quick_view_triggers_present(client):
    """Each project card must have a Quick View trigger and embedded project JSON."""
    response = client.get("/explore")
    assert response.status_code == 200
    assert b'data-quick-view="' in response.data
    assert b'data-project-json="' in response.data


def test_active_filters_ribbon_appears_when_filtered(client):
    """Active filters ribbon must render when a filter query is active."""
    # Without filters
    res_no_filter = client.get("/explore")
    assert b'class="active-filters-bar"' not in res_no_filter.data

    # With search filter
    res_filtered = client.get("/explore?search=python")
    assert b'class="active-filters-bar"' in res_filtered.data
    assert b'Search: "python"' in res_filtered.data
