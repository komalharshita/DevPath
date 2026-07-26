"""
Tests for the DevPath Sentinel dataset validator.
"""

from __future__ import annotations

import json

from tools.sentinel.validators.dataset_validator import run


def create_project(**overrides):
    """Create a valid project dictionary."""

    project = {
        "id": 1,
        "title": "Expense Tracker",
        "skills": ["Python"],
        "level": "Beginner",
        "interest": "Finance",
        "time": "2 weeks",
        "description": "Track expenses.",
        "features": [
            "Add expense",
            "Delete expense",
        ],
        "roadmap": [
            "Planning",
            "Implementation",
        ],
        "resources": [
            "https://python.org",
        ],
        "starter_code": "starter_code/expense_tracker.py",
    }

    project.update(overrides)
    return project


def write_dataset(tmp_path, projects):
    """Create a temporary projects.json file."""

    data_dir = tmp_path / "data"
    data_dir.mkdir()

    dataset_path = data_dir / "projects.json"

    dataset_path.write_text(
        json.dumps(projects, indent=2),
        encoding="utf-8",
    )

    return dataset_path


def create_starter_file(tmp_path, filename):
    """Create a starter code file."""

    starter_dir = tmp_path / "starter_code"
    starter_dir.mkdir(exist_ok=True)

    (starter_dir / filename).write_text(
        "# starter code",
        encoding="utf-8",
    )


def test_valid_dataset(tmp_path):
    """A valid dataset should pass validation."""

    create_starter_file(
        tmp_path,
        "expense_tracker.py",
    )

    dataset = write_dataset(
        tmp_path,
        [create_project()],
    )

    result = run(dataset)

    assert result.passed is True
    assert result.errors == []
    assert result.warnings == []


def test_duplicate_project_ids(tmp_path):
    """Duplicate IDs should produce an error."""

    create_starter_file(
        tmp_path,
        "expense_tracker.py",
    )

    dataset = write_dataset(
        tmp_path,
        [
            create_project(id=1),
            create_project(
                id=1,
                title="Calculator",
            ),
        ],
    )

    result = run(dataset)

    assert result.passed is False

    assert any(
        "Duplicate project ID"
        in error
        for error in result.errors
    )


def test_duplicate_project_titles(tmp_path):
    """Duplicate titles should produce an error."""

    create_starter_file(
        tmp_path,
        "expense_tracker.py",
    )

    dataset = write_dataset(
        tmp_path,
        [
            create_project(id=1),
            create_project(id=2),
        ],
    )

    result = run(dataset)

    assert result.passed is False

    assert any(
        "Duplicate project title"
        in error
        for error in result.errors
    )


def test_missing_required_field(tmp_path):
    """Missing required fields should fail validation."""

    create_starter_file(
        tmp_path,
        "expense_tracker.py",
    )

    project = create_project()

    del project["description"]

    dataset = write_dataset(
        tmp_path,
        [project],
    )

    result = run(dataset)

    assert result.passed is False

    assert any(
        "missing required fields"
        in error
        for error in result.errors
    )


def test_empty_required_field(tmp_path):
    """Empty required string fields should fail validation."""

    create_starter_file(
        tmp_path,
        "expense_tracker.py",
    )

    dataset = write_dataset(
        tmp_path,
        [
            create_project(
                title="",
            ),
        ],
    )

    result = run(dataset)

    assert result.passed is False

    assert any(
        "empty 'title'"
        in error
        for error in result.errors
    )


def test_missing_starter_code_warning(tmp_path):
    """Missing starter code should produce a warning."""

    dataset = write_dataset(
        tmp_path,
        [create_project()],
    )

    result = run(dataset)

    assert result.passed is True
    assert result.errors == []
    assert len(result.warnings) == 1

    assert "[1]" in result.warnings[0]


def test_invalid_json(tmp_path):
    """Invalid JSON should fail validation."""

    data_dir = tmp_path / "data"
    data_dir.mkdir()

    dataset = data_dir / "projects.json"

    dataset.write_text(
        "{ invalid json",
        encoding="utf-8",
    )

    result = run(dataset)

    assert result.passed is False

    assert any(
        "Invalid JSON"
        in error
        for error in result.errors
    )


def test_missing_dataset_file(tmp_path):
    """Missing dataset file should fail validation."""

    dataset = (
        tmp_path
        / "data"
        / "projects.json"
    )

    result = run(dataset)

    assert result.passed is False

    assert any(
        "Dataset not found"
        in error
        for error in result.errors
    )