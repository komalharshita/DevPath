import pytest
from models import Project
from routes.main_routes import find_project_by_id

def test_project_model_includes_estimated_hours():
    project = Project(
        title="Test Project",
        level="Beginner",
        interest="Web",
        time="Low",
        description="A test project",
        estimated_hours=8.5
    )
    p_dict = project.to_dict()
    assert "estimated_hours" in p_dict
    assert p_dict["estimated_hours"] == 8.5

def test_seeded_project_has_estimated_hours():
    project = find_project_by_id(1)
    assert project is not None
    assert "estimated_hours" in project
    assert project["estimated_hours"] > 0
