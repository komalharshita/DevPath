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


def test_multiple_duplicate_project_ids(tmp_path):
    """Multiple duplicate IDs should all be reported."""

    create_starter_file(
        tmp_path,
        "expense_tracker.py",
    )

    dataset = write_dataset(
        tmp_path,
        [
            create_project(
                id=1,
                title="Expense Tracker",
            ),
            create_project(
                id=1,
                title="Calculator",
            ),
            create_project(
                id=2,
                title="Weather App",
            ),
            create_project(
                id=2,
                title="Todo App",
            ),
        ],
    )

    result = run(dataset)

    assert result.passed is False

    assert result.errors == [
        "Duplicate project ID: 1",
        "Duplicate project ID: 2",
    ]


def test_multiple_duplicate_project_titles(tmp_path):
    """Multiple duplicate titles should all be reported."""

    create_starter_file(
        tmp_path,
        "expense_tracker.py",
    )

    dataset = write_dataset(
        tmp_path,
        [
            create_project(
                id=1,
                title="Calculator",
            ),
            create_project(
                id=2,
                title="Calculator",
            ),
            create_project(
                id=3,
                title="Todo App",
            ),
            create_project(
                id=4,
                title="Todo App",
            ),
        ],
    )

    result = run(dataset)

    assert result.passed is False

    assert result.errors == [
        'Duplicate project title: "Calculator"',
        'Duplicate project title: "Todo App"',
    ]


def test_whitespace_only_required_field(tmp_path):
    """Whitespace-only required fields should fail validation."""

    create_starter_file(
        tmp_path,
        "expense_tracker.py",
    )

    dataset = write_dataset(
        tmp_path,
        [
            create_project(
                title="   ",
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


def test_empty_required_list_field(tmp_path):
    """Empty required list fields should fail validation."""

    create_starter_file(
        tmp_path,
        "expense_tracker.py",
    )

    dataset = write_dataset(
        tmp_path,
        [
            create_project(
                skills=[],
            ),
        ],
    )

    result = run(dataset)

    assert result.passed is False

    assert any(
        "empty 'skills'"
        in error
        for error in result.errors
    )


def test_multiple_missing_required_fields(tmp_path):
    """Multiple missing required fields should all be reported."""

    create_starter_file(
        tmp_path,
        "expense_tracker.py",
    )

    project = create_project()

    del project["description"]
    del project["features"]
    del project["resources"]

    dataset = write_dataset(
        tmp_path,
        [project],
    )

    result = run(dataset)

    assert result.passed is False

    assert len(result.errors) == 1

    assert (
        "Project 1 is missing required fields: "
        "description, features, resources"
        in result.errors[0]
    )


def test_multiple_validation_failures(tmp_path):
    """Multiple validation checks should be reported together."""

    create_starter_file(
        tmp_path,
        "expense_tracker.py",
    )

    project_one = create_project(
        id=1,
        title="Calculator",
    )

    project_two = create_project(
        id=1,
        title="Calculator",
        skills=[],
    )

    del project_two["description"]

    dataset = write_dataset(
        tmp_path,
        [
            project_one,
            project_two,
        ],
    )

    result = run(dataset)

    assert result.passed is False

    assert any(
        "Duplicate project ID: 1"
        in error
        for error in result.errors
    )

    assert any(
        'Duplicate project title: "Calculator"'
        in error
        for error in result.errors
    )

    assert any(
        "missing required fields: description"
        in error
        for error in result.errors
    )

    assert any(
        "empty 'skills'"
        in error
        for error in result.errors
    )


def test_duplicate_values_are_reported_in_sorted_order(tmp_path):
    """Duplicate IDs and titles should be reported deterministically."""

    create_starter_file(
        tmp_path,
        "expense_tracker.py",
    )

    dataset = write_dataset(
        tmp_path,
        [
            create_project(
                id=3,
                title="Zebra App",
            ),
            create_project(
                id=1,
                title="Alpha App",
            ),
            create_project(
                id=3,
                title="Zebra App",
            ),
            create_project(
                id=1,
                title="Alpha App",
            ),
        ],
    )

    result = run(dataset)

    assert result.passed is False

    assert result.errors == [
        "Duplicate project ID: 1",
        "Duplicate project ID: 3",
        'Duplicate project title: "Alpha App"',
        'Duplicate project title: "Zebra App"',
    ]
