# tests/test_portfolio_analyzer.py
# Smoke tests for utils/portfolio_analyzer.py.
#
# These exist because a "remove unused import" cleanup once deleted the
# `import re` that _build_keyword_pattern() depends on, which made every
# deployment that imports `app` fail with NameError.  Importing the module
# (and the Flask app, which imports it) must never raise.

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from utils.portfolio_analyzer import analyze_portfolio


def test_app_imports_portfolio_analyzer():
    """Importing the Flask app must succeed (it imports portfolio_analyzer)."""
    from app import app
    assert app is not None


def test_analyze_portfolio_returns_expected_structure():
    """analyze_portfolio must return the documented keys for a valid input."""
    result = analyze_portfolio([
        {
            "title": "Weather Dashboard",
            "description": "A REST API weather app",
            "skills": ["Python", "Flask"],
            "tech_stack": ["Flask"],
            "features": [],
        }
    ])
    assert result["score"] >= 0
    assert isinstance(result["covered"], list)
    assert isinstance(result["missing"], list)
    assert isinstance(result["categories"], list)
    assert isinstance(result["recommendations"], list)


def test_keyword_patterns_match_expected_domains():
    """The compiled regex patterns must still match (re must be imported)."""
    result = analyze_portfolio([
        {
            "title": "CI/CD pipeline with GitHub Actions",
            "description": "docker deploy",
            "skills": ["Python", "Docker"],
            "tech_stack": [],
            "features": [],
        }
    ])
    assert "DevOps" in result["covered"]
    assert "Deployment" in result["covered"]
