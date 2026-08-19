# tests/test_recommender_tech_stack.py
# Regression test for issue #1870:
# The technology stack filter must actually narrow the recommendations returned
# by get_recommendations (project_matches_tech was defined but never called).

from utils.recommender import get_recommendations, project_matches_tech


def test_all_returns_everything():
    """With tech_stack='all' the filter must not exclude any project."""
    results = get_recommendations("Python", "Beginner", "Data", "Low", tech_stack="all")
    assert len(results["recommendations"]) > 0


def test_tech_stack_filter_changes_results():
    """A non-'all' tech stack must produce a different recommendation set."""
    base = get_recommendations("Python", "Beginner", "Data", "Low", tech_stack="all")
    filtered = get_recommendations("Java", "Beginner", "Web", "Low", tech_stack="java")
    base_ids = [p["id"] for p in base["recommendations"]]
    filtered_ids = [p["id"] for p in filtered["recommendations"]]
    assert filtered_ids != base_ids, (
        "tech_stack filter had no effect (issue #1870)"
    )


def test_filtered_projects_actually_match_tech():
    """Every project returned for a given tech_stack must match it."""
    filtered = get_recommendations("Java", "Beginner", "Web", "Low", tech_stack="java")
    assert filtered["recommendations"], "Expected at least one java project to match"
    for project in filtered["recommendations"]:
        assert project_matches_tech(project, "java"), (
            f"Project {project.get('id')} does not match tech_stack='java' (issue #1870)"
        )


def test_filtered_results_are_subset_of_all():
    """Filtered results must never include projects that fail the tech stack filter."""
    filtered = get_recommendations("Python", "Beginner", "Data", "Low", tech_stack="python")
    for project in filtered["recommendations"]:
        assert project_matches_tech(project, "python"), (
            f"Project {project.get('id')} returned by filter but does not match tech_stack='python'"
        )
