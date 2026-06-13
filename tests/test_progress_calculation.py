# tests/test_progress_calculation.py
# Tests for bug #738 — Learning Progress calculation fix.
#
# The original bug: progress percentage was computed as
#   (points / 250) * 100
# where 250 was an arbitrary hardcoded cap too low for normal usage.
# A user with 10 searches, 10 views, 5 code opens, 5 completions would
# accumulate 10*5 + 10*10 + 5*15 + 5*30 = 50+100+75+150 = 375 points,
# giving 375/250*100 = 150% before the Math.min(100) clamp.
# While the display was clamped, aria-valuenow received 150 — an
# accessibility violation (ARIA spec requires progressbar valuenow <= valuemax).
#
# The fix: derive PROGRESS_MAX_POINTS from the defined per-action weights
# and targets so the denominator always matches the actual scoring formula.
#
# Run with:  python -m pytest tests/test_progress_calculation.py -v

import sys
import os
import re

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


@pytest.fixture
def js(client):
    """Return the decoded content of static/script.js."""
    response = client.get("/static/script.js")
    assert response.status_code == 200
    return response.data.decode("utf-8")


# ---------------------------------------------------------------------------
# Constant definitions present in script.js
# ---------------------------------------------------------------------------

def test_points_per_search_defined(js):
    assert "POINTS_PER_SEARCH" in js, "POINTS_PER_SEARCH constant must be defined"

def test_points_per_view_defined(js):
    assert "POINTS_PER_VIEW" in js, "POINTS_PER_VIEW constant must be defined"

def test_points_per_code_open_defined(js):
    assert "POINTS_PER_CODE_OPEN" in js, "POINTS_PER_CODE_OPEN constant must be defined"

def test_points_per_completion_defined(js):
    assert "POINTS_PER_COMPLETION" in js, "POINTS_PER_COMPLETION constant must be defined"

def test_progress_max_points_defined(js):
    assert "PROGRESS_MAX_POINTS" in js, (
        "PROGRESS_MAX_POINTS must be defined so the denominator in the "
        "percentage formula is derived from the scoring weights, not a "
        "hardcoded magic number"
    )

def test_magic_number_250_removed(js):
    """The hardcoded magic-number cap 250 must no longer appear in the
    percentage formula.  It may still appear in unrelated contexts (e.g.
    string literals) but must not be used as the divisor."""
    # Find the percentage computation line
    # We look for the pattern: points / <number> * 100  or  points / <number>) * 100
    magic = re.findall(r"progress\.points\s*/\s*250", js)
    assert len(magic) == 0, (
        "progress.points / 250 still present — replace with "
        "progress.points / PROGRESS_MAX_POINTS"
    )

def test_progress_max_points_used_as_divisor(js):
    """PROGRESS_MAX_POINTS must appear as the divisor in the percentage line."""
    assert "progress.points / PROGRESS_MAX_POINTS" in js or \
           "progress.points/PROGRESS_MAX_POINTS" in js, (
        "Percentage formula must divide by PROGRESS_MAX_POINTS"
    )


# ---------------------------------------------------------------------------
# Arithmetic correctness (Python mirror of the JS scoring logic)
# These tests replicate the JS constants and formula in Python so we can
# assert exact numeric outcomes without a browser runtime.
# ---------------------------------------------------------------------------

# Mirror of the JS constants (must stay in sync with script.js)
POINTS_PER_SEARCH     = 5
POINTS_PER_VIEW       = 10
POINTS_PER_CODE_OPEN  = 15
POINTS_PER_COMPLETION = 30

PROGRESS_TARGET_SEARCHES    = 10
PROGRESS_TARGET_VIEWS       = 10
PROGRESS_TARGET_CODE_OPENS  = 10
PROGRESS_TARGET_COMPLETIONS = 5

PROGRESS_MAX_POINTS = (
    PROGRESS_TARGET_SEARCHES    * POINTS_PER_SEARCH     +
    PROGRESS_TARGET_VIEWS       * POINTS_PER_VIEW       +
    PROGRESS_TARGET_CODE_OPENS  * POINTS_PER_CODE_OPEN  +
    PROGRESS_TARGET_COMPLETIONS * POINTS_PER_COMPLETION
)


def compute_points(searches, views, code_opens, completions):
    raw = (searches      * POINTS_PER_SEARCH     +
           views         * POINTS_PER_VIEW       +
           code_opens    * POINTS_PER_CODE_OPEN  +
           completions   * POINTS_PER_COMPLETION)
    return min(raw, PROGRESS_MAX_POINTS)


def compute_percentage(points):
    return min(100, round((points / PROGRESS_MAX_POINTS) * 100))


def test_max_points_value():
    """PROGRESS_MAX_POINTS must equal 450 given the defined targets."""
    assert PROGRESS_MAX_POINTS == 450, (
        f"Expected 450, got {PROGRESS_MAX_POINTS}. "
        "10*5 + 10*10 + 10*15 + 5*30 = 50+100+150+150 = 450"
    )


def test_zero_activity_gives_zero_points():
    points = compute_points(0, 0, 0, 0)
    assert points == 0


def test_zero_activity_gives_zero_percent():
    assert compute_percentage(0) == 0


def test_single_search_correct_points():
    points = compute_points(searches=1, views=0, code_opens=0, completions=0)
    assert points == POINTS_PER_SEARCH


def test_single_search_correct_percentage():
    points = compute_points(searches=1, views=0, code_opens=0, completions=0)
    pct = compute_percentage(points)
    expected = round((POINTS_PER_SEARCH / PROGRESS_MAX_POINTS) * 100)
    assert pct == expected


def test_previous_bug_scenario_does_not_exceed_100_percent():
    """The exact scenario that triggered the original bug:
    a moderately active user whose raw points exceeded the old 250 cap."""
    # Raw = 10*5 + 10*10 + 5*15 + 5*30 = 50+100+75+150 = 375
    # Old formula: 375/250*100 = 150% (bug)
    # New formula: min(375, 450) = 375; 375/450*100 = 83%
    points = compute_points(searches=10, views=10, code_opens=5, completions=5)
    pct = compute_percentage(points)
    assert pct <= 100, f"Percentage must never exceed 100, got {pct}"
    assert pct == 83, f"Expected 83%, got {pct}%"


def test_at_target_activity_gives_100_percent():
    """Reaching all targets exactly must give exactly 100%."""
    points = compute_points(
        searches=PROGRESS_TARGET_SEARCHES,
        views=PROGRESS_TARGET_VIEWS,
        code_opens=PROGRESS_TARGET_CODE_OPENS,
        completions=PROGRESS_TARGET_COMPLETIONS
    )
    assert points == PROGRESS_MAX_POINTS
    assert compute_percentage(points) == 100


def test_exceeding_all_targets_clamped_to_100_percent():
    """Exceeding every target must still give 100%, not over."""
    points = compute_points(
        searches=PROGRESS_TARGET_SEARCHES * 10,
        views=PROGRESS_TARGET_VIEWS * 10,
        code_opens=PROGRESS_TARGET_CODE_OPENS * 10,
        completions=PROGRESS_TARGET_COMPLETIONS * 10
    )
    assert points == PROGRESS_MAX_POINTS, "Points must be clamped at max"
    assert compute_percentage(points) == 100


def test_completions_weighted_highest():
    """A single completion must score more points than a single search."""
    assert POINTS_PER_COMPLETION > POINTS_PER_SEARCH


def test_code_open_weighted_more_than_view():
    """Opening code must score more than just viewing a project."""
    assert POINTS_PER_CODE_OPEN > POINTS_PER_VIEW


def test_percentage_never_negative():
    """Points can never be negative — percentage must always be >= 0."""
    assert compute_percentage(0) >= 0


def test_percentage_is_integer():
    """Percentage must be a whole number (Math.round in JS)."""
    for searches in range(0, 12, 3):
        for completions in range(0, 6, 2):
            points = compute_points(searches, 0, 0, completions)
            pct = compute_percentage(points)
            assert isinstance(pct, int), f"Expected int, got {type(pct)} for {pct}"


def test_incremental_searches_increase_percentage():
    """Each additional search must increase or hold the percentage."""
    previous = 0
    for n in range(1, PROGRESS_TARGET_SEARCHES + 1):
        points = compute_points(searches=n, views=0, code_opens=0, completions=0)
        pct = compute_percentage(points)
        assert pct >= previous, f"Percentage dropped from {previous} to {pct} at {n} searches"
        previous = pct


def test_aria_valuenow_never_exceeds_100():
    """aria-valuenow must always be in [0, 100] per ARIA spec.
    This was the accessibility violation in the original bug."""
    for s in range(0, 20, 4):
        for c in range(0, 10, 2):
            points = compute_points(s, s, s, c)
            pct = compute_percentage(points)
            assert 0 <= pct <= 100, (
                f"aria-valuenow={pct} is out of [0,100] range for "
                f"searches={s}, completions={c}"
            )


# ---------------------------------------------------------------------------
# HTML — progressbar ARIA attributes are correct
# ---------------------------------------------------------------------------

def test_progressbar_role_present(client):
    r = client.get("/")
    assert b'role="progressbar"' in r.data


def test_progressbar_aria_valuemin_zero(client):
    r = client.get("/")
    assert b'aria-valuemin="0"' in r.data


def test_progressbar_aria_valuemax_100(client):
    """aria-valuemax must be 100 — matches the percentage scale."""
    r = client.get("/")
    assert b'aria-valuemax="100"' in r.data


def test_progressbar_initial_aria_valuenow_zero(client):
    """On initial page load aria-valuenow must be 0."""
    r = client.get("/")
    assert b'aria-valuenow="0"' in r.data


# ---------------------------------------------------------------------------
# Security headers unchanged
# ---------------------------------------------------------------------------

def test_security_headers_on_homepage(client):
    r = client.get("/")
    assert r.headers.get("X-Frame-Options") == "DENY"
    assert r.headers.get("X-Content-Type-Options") == "nosniff"
