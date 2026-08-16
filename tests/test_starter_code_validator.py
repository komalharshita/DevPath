"""
Tests for the DevPath Sentinel Starter Code Integrity Validator.
"""

from __future__ import annotations

import json

from tools.sentinel.validators.starter_code_validator import run


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


def create_starter_file(
    tmp_path,
    filename,
    *,
    content="# starter code",
):
    """Create a starter code file."""

    starter_dir = tmp_path / "starter_code"
    starter_dir.mkdir(exist_ok=True)

    file_path = starter_dir / filename

    file_path.write_text(
        content,
        encoding="utf-8",
    )

    return file_path


def test_valid_starter_code(tmp_path):
    """A valid starter code directory should pass validation."""

    create_starter_file(
        tmp_path,
        "expense_tracker.py",
    )

    dataset = write_dataset(
        tmp_path,
        [create_project()],
    )

    result = run(
        dataset_path=dataset,
        starter_code_dir=tmp_path / "starter_code",
    )

    assert result.name == "Starter Code Integrity Validator"

    assert result.passed is True
    assert result.errors == []
    assert result.warnings == []

    assert result.details["resource"] == "Starter Code Files"
    assert result.details["count"] == 1

    checks = result.details["checks"]

    assert checks["orphan_files"] == []
    assert checks["empty_files"] == []
    assert checks["hidden_files"] == []
    assert checks["unsupported_extensions"] == []

    metadata = result.details["metadata"]

    assert metadata["orphan_files"]["severity"] == "error"
    assert metadata["empty_files"]["severity"] == "error"
    assert metadata["hidden_files"]["severity"] == "warning"
    assert metadata["unsupported_extensions"]["severity"] == "warning"


def test_orphan_files(tmp_path):
    """Orphan starter code files should produce an error."""

    create_starter_file(
        tmp_path,
        "expense_tracker.py",
    )

    create_starter_file(
        tmp_path,
        "calculator.py",
    )

    dataset = write_dataset(
        tmp_path,
        [create_project()],
    )

    result = run(
        dataset_path=dataset,
        starter_code_dir=tmp_path / "starter_code",
    )

    assert result.passed is False

    assert any(
        "Orphan Files"
        in error
        for error in result.errors
    )

    assert result.details["checks"]["orphan_files"] == [
        "starter_code/calculator.py",
    ]


def test_empty_files(tmp_path):
    """Empty starter code files should produce an error."""

    create_starter_file(
        tmp_path,
        "expense_tracker.py",
        content="",
    )

    dataset = write_dataset(
        tmp_path,
        [create_project()],
    )

    result = run(
        dataset_path=dataset,
        starter_code_dir=tmp_path / "starter_code",
    )

    assert result.passed is False

    assert any(
        "Empty Files"
        in error
        for error in result.errors
    )

    assert result.details["checks"]["empty_files"] == [
        "starter_code/expense_tracker.py",
    ]


def test_hidden_files(tmp_path):
    """Hidden starter code files should produce a warning."""

    create_starter_file(
        tmp_path,
        "expense_tracker.py",
    )

    create_starter_file(
        tmp_path,
        ".gitkeep",
    )

    dataset = write_dataset(
        tmp_path,
        [create_project()],
    )

    result = run(
        dataset_path=dataset,
        starter_code_dir=tmp_path / "starter_code",
    )

    assert result.passed is False

    assert any(
        "Orphan Files"
        in error
        for error in result.errors
    )

    assert len(result.warnings) == 2

    assert any(
        "Hidden Files"
        in warning
        for warning in result.warnings
    )

    assert any(
        "Unsupported Extensions"
        in warning
        for warning in result.warnings
    )

    assert any(
        "Hidden Files"
        in warning
        for warning in result.warnings
    )

    assert result.details["checks"]["hidden_files"] == [
        "starter_code/.gitkeep",
    ]

    print(result.errors)
    print(result.warnings)
    print(result.details)


def test_unsupported_extensions(tmp_path):
    """Unsupported starter code files should produce a warning."""

    create_starter_file(
        tmp_path,
        "expense_tracker.py",
    )

    create_starter_file(
        tmp_path,
        "notes.pdf",
    )

    dataset = write_dataset(
        tmp_path,
        [create_project()],
    )

    result = run(
        dataset_path=dataset,
        starter_code_dir=tmp_path / "starter_code",
    )

    assert result.passed is False

    assert any(
        "Orphan Files"
        in error
        for error in result.errors
    )

    assert len(result.warnings) == 1

    assert any(
        "Unsupported Extensions"
        in warning
        for warning in result.warnings
    )

    assert any(
        "Unsupported Extensions"
        in warning
        for warning in result.warnings
    )

    assert result.details["checks"]["unsupported_extensions"] == [
        "starter_code/notes.pdf",
    ]


def test_invalid_json(tmp_path):
    """Invalid JSON should fail validation."""

    data_dir = tmp_path / "data"
    data_dir.mkdir()

    dataset = data_dir / "projects.json"

    dataset.write_text(
        "{ invalid json",
        encoding="utf-8",
    )

    result = run(
        dataset_path=dataset,
        starter_code_dir=tmp_path / "starter_code",
    )

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

    result = run(
        dataset_path=dataset,
        starter_code_dir=tmp_path / "starter_code",
    )

    assert result.passed is False

    assert any(
        "Dataset file not found"
        in error
        for error in result.errors
    )


def test_missing_starter_code_directory(tmp_path):
    """Missing starter code directory should fail validation."""

    dataset = write_dataset(
        tmp_path,
        [create_project()],
    )

    result = run(
        dataset_path=dataset,
        starter_code_dir=tmp_path / "starter_code",
    )

    assert result.passed is False

    assert any(
        "Starter code directory not found"
        in error
        for error in result.errors
    )


def test_nested_starter_code_file(tmp_path):
    """Nested starter code files should be discovered and validated."""

    nested_dir = tmp_path / "starter_code" / "python"
    nested_dir.mkdir(parents=True)

    file_path = nested_dir / "expense_tracker.py"
    file_path.write_text(
        "# starter code",
        encoding="utf-8",
    )

    dataset = write_dataset(
        tmp_path,
        [
            create_project(
                starter_code="starter_code/python/expense_tracker.py",
            ),
        ],
    )

    result = run(
        dataset_path=dataset,
        starter_code_dir=tmp_path / "starter_code",
    )

    assert result.passed is True
    assert result.errors == []
    assert result.warnings == []

    assert result.details["checks"]["orphan_files"] == []

    assert result.details["count"] == 1


def test_nested_orphan_file(tmp_path):
    """Nested unreferenced starter code files should be detected."""

    nested_dir = tmp_path / "starter_code" / "python"
    nested_dir.mkdir(parents=True)

    (nested_dir / "expense_tracker.py").write_text(
        "# starter code",
        encoding="utf-8",
    )

    (nested_dir / "calculator.py").write_text(
        "# orphan starter code",
        encoding="utf-8",
    )

    dataset = write_dataset(
        tmp_path,
        [
            create_project(
                starter_code="starter_code/python/expense_tracker.py",
            ),
        ],
    )

    result = run(
        dataset_path=dataset,
        starter_code_dir=tmp_path / "starter_code",
    )

    assert result.passed is False

    assert result.details["checks"]["orphan_files"] == [
        "starter_code/python/calculator.py",
    ]

    assert any(
        "Orphan Files"
        in error
        for error in result.errors
    )


def test_multiple_empty_files(tmp_path):
    """Multiple empty starter code files should all be detected."""

    create_starter_file(
        tmp_path,
        "expense_tracker.py",
        content="",
    )

    create_starter_file(
        tmp_path,
        "calculator.py",
        content="",
    )

    dataset = write_dataset(
        tmp_path,
        [
            create_project(
                starter_code="starter_code/expense_tracker.py",
            ),
            create_project(
                id=2,
                title="Calculator",
                starter_code="starter_code/calculator.py",
            ),
        ],
    )

    result = run(
        dataset_path=dataset,
        starter_code_dir=tmp_path / "starter_code",
    )

    assert result.passed is False

    assert result.details["checks"]["empty_files"] == [
        "starter_code/calculator.py",
        "starter_code/expense_tracker.py",
    ]

    assert any(
        "Empty Files"
        in error
        for error in result.errors
    )


def test_multiple_hidden_files(tmp_path):
    """Multiple hidden files should all produce a warning."""

    create_starter_file(
        tmp_path,
        ".gitkeep",
    )

    create_starter_file(
        tmp_path,
        ".config",
    )

    dataset = write_dataset(
        tmp_path,
        [create_project()],
    )

    result = run(
        dataset_path=dataset,
        starter_code_dir=tmp_path / "starter_code",
    )

    assert result.passed is False

    assert len(result.warnings) == 2

    assert result.details["checks"]["hidden_files"] == [
        "starter_code/.config",
        "starter_code/.gitkeep",
    ]

    assert any(
        "Hidden Files"
        in warning
        for warning in result.warnings
    )


def test_multiple_unsupported_extensions(tmp_path):
    """Multiple unsupported file types should all produce warnings."""

    create_starter_file(
        tmp_path,
        "expense_tracker.py",
    )

    create_starter_file(
        tmp_path,
        "notes.pdf",
    )

    create_starter_file(
        tmp_path,
        "archive.zip",
    )

    dataset = write_dataset(
        tmp_path,
        [create_project()],
    )

    result = run(
        dataset_path=dataset,
        starter_code_dir=tmp_path / "starter_code",
    )

    assert result.passed is False

    assert result.details["checks"]["unsupported_extensions"] == [
        "starter_code/archive.zip",
        "starter_code/notes.pdf",
    ]

    assert any(
        "Unsupported Extensions"
        in warning
        for warning in result.warnings
    )


def test_all_supported_extensions(tmp_path):
    """All configured supported extensions should pass validation."""

    supported_extensions = [
        ".py",
        ".js",
        ".java",
        ".html",
        ".css",
        ".yml",
        ".yaml",
        ".txt",
        ".md",
    ]

    starter_dir = tmp_path / "starter_code"
    starter_dir.mkdir()

    projects = []

    for index, extension in enumerate(supported_extensions, start=1):
        filename = f"project_{index}{extension}"

        (starter_dir / filename).write_text(
            "# starter code",
            encoding="utf-8",
        )

        projects.append(
            create_project(
                id=index,
                title=f"Project {index}",
                starter_code=f"starter_code/{filename}",
            )
        )

    dataset = write_dataset(
        tmp_path,
        projects,
    )

    result = run(
        dataset_path=dataset,
        starter_code_dir=starter_dir,
    )

    assert result.passed is True
    assert result.errors == []
    assert result.warnings == []

    assert result.details["checks"]["unsupported_extensions"] == []
    assert result.details["checks"]["orphan_files"] == []

    assert result.details["count"] == len(supported_extensions)


def test_dataset_must_be_json_array(tmp_path):
    """A JSON object instead of a project list should fail validation."""

    data_dir = tmp_path / "data"
    data_dir.mkdir()

    dataset = data_dir / "projects.json"

    dataset.write_text(
        json.dumps(
            {
                "project": create_project(),
            }
        ),
        encoding="utf-8",
    )

    result = run(
        dataset_path=dataset,
        starter_code_dir=tmp_path / "starter_code",
    )

    assert result.passed is False

    assert any(
        "Dataset must contain a JSON array of projects."
        in error
        for error in result.errors
    )
