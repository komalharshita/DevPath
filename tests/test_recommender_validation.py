import os
import sys


sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils.recommender import validate_recommendation_inputs


def test_validate_recommendation_inputs_accepts_supported_interests():
    errors = validate_recommendation_inputs("Python", "Beginner", "Web", "Low")

    assert errors == []


def test_validate_recommendation_inputs_accepts_interest_case_insensitively():
    errors = validate_recommendation_inputs("Python", "Beginner", "machine learning/ai", "Low")

    assert errors == []


def test_validate_recommendation_inputs_rejects_unknown_interest():
    errors = validate_recommendation_inputs("Python", "Beginner", "Unknown", "Low")

    assert "Please select a valid area of interest." in errors
