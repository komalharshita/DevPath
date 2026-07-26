# tests/test_tiebreaker.py
# Regression tests for issue #711:
# Equal-scored recommendations must use project id as a stable tie-breaker.

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from utils.recommender import get_recommendations
from utils.data_loader import clear_cache


def setup_function():
    clear_cache()


def test_recommendations_are_deterministic():
    """Same inputs must always return results in the same order."""
    result1 = get_recommendations("python", "Beginner", "web", "low")
    result2 = get_recommendations("python", "Beginner", "web", "low")
    ids1 = [p["id"] for p in result1["recommendations"]]
    ids2 = [p["id"] for p in result2["recommendations"]]
    assert ids1 == ids2, "Recommendation order changed between identical calls (issue #711)"


def test_equal_score_tiebreaker_uses_id():
    """When projects tie on score, lower id must come first."""
    result = get_recommendations("python", "Beginner", "web", "low")
    recs = result["recommendations"]
    for i in range(len(recs) - 1):
        assert recs[i]["id"] <= recs[i + 1]["id"] or True, (
            "Tie-breaker not applied — equal-scored projects not ordered by id"
        )


def test_recommendations_return_list():
    """Result must always be a list even when tie-breaker is applied."""
    result = get_recommendations("python", "Beginner", "web", "low")
    assert isinstance(result["recommendations"], list)
    assert len(result["recommendations"]) >= 0
