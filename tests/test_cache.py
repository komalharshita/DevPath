# tests/test_cache.py
# Regression tests for issue #709

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from utils.data_loader import load_all_projects, clear_cache


def setup_function():
    clear_cache()


def test_cache_returns_same_object_on_second_call():
    first = load_all_projects()
    second = load_all_projects()
    assert first is second, "load_all_projects() re-reads file instead of returning cache (issue #709)"


def test_clear_cache_forces_fresh_load():
    first = load_all_projects()
    clear_cache()
    second = load_all_projects()
    assert first is not second
    assert first == second


def test_cache_content_is_valid_project_list():
    projects = load_all_projects()
    assert isinstance(projects, list)
    assert len(projects) > 0
    assert all(isinstance(p, dict) for p in projects)
