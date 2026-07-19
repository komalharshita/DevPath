"""
Dataset validation utilities for DevPath Sentinel.
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

from tools.sentinel.models import ValidationResult


REPO_ROOT = Path(__file__).resolve().parents[3]

DATASET_PATH = REPO_ROOT / "data" / "projects.json"

REQUIRED_FIELDS = (
    "id",
    "title",
    "skills",
    "level",
    "interest",
    "time",
    "description",
    "features",
    "roadmap",
    "resources",
    "starter_code",
)


def _load_projects(dataset_path: Path) -> list[dict[str, Any]]:
    """
    Load a project dataset from disk.
    """

    with dataset_path.open("r", encoding="utf-8") as file:
        return json.load(file)


def _validate_duplicate_ids(
    projects: list[dict[str, Any]],
) -> list[str]:
    """
    Find duplicate project IDs.
    """

    ids = [
        project.get("id")
        for project in projects
    ]

    duplicates = [
        str(project_id)
        for project_id, count in Counter(ids).items()
        if count > 1
    ]

    return [
        f"Duplicate project ID: {project_id}"
        for project_id in sorted(duplicates)
    ]


def _validate_duplicate_titles(
    projects: list[dict[str, Any]],
) -> list[str]:
    """
    Find duplicate project titles.
    """

    titles = [
        project.get("title", "").strip()
        for project in projects
    ]

    duplicates = [
        title
        for title, count in Counter(titles).items()
        if count > 1
    ]

    return [
        f'Duplicate project title: "{title}"'
        for title in sorted(duplicates)
    ]


def _validate_required_fields(
    projects: list[dict[str, Any]],
) -> list[str]:
    """
    Ensure every project contains all required fields.
    """

    errors: list[str] = []

    for project in projects:

        project_id = project.get("id", "UNKNOWN")

        missing_fields = [
            field
            for field in REQUIRED_FIELDS
            if field not in project
        ]

        if missing_fields:

            errors.append(
                (
                    f"Project {project_id} "
                    f"is missing required fields: "
                    f"{', '.join(missing_fields)}"
                )
            )

    return errors

def _validate_empty_fields(
    projects: list[dict[str, Any]],
) -> list[str]:
    """
    Ensure required fields are not empty.
    """

    errors: list[str] = []

    for project in projects:

        project_id = project.get("id", "UNKNOWN")

        for field in REQUIRED_FIELDS:

            value = project.get(field)

            if value is None:
                continue

            if isinstance(value, str) and not value.strip():
                errors.append(
                    f"Project {project_id} has an empty '{field}' field."
                )

            elif isinstance(value, list) and not value:
                errors.append(
                    f"Project {project_id} has an empty '{field}' field."
                )

    return errors


def _validate_starter_code(
    projects: list[dict[str, Any]],
    repository_root: Path,
) -> list[str]:
    """
    Verify starter code files exist.
    """

    warnings: list[str] = []

    for project in projects:

        project_id = project.get("id", "UNKNOWN")

        starter_code = project.get("starter_code")

        if not starter_code:
            continue

        starter_path = repository_root / starter_code

        if not starter_path.is_file():
            warnings.append(
                (
                    f"[{project_id}] {starter_code}"
                )
            )

    return warnings


def run(
    dataset_path: Path | None = None,
) -> ValidationResult:
    """
    Execute all dataset validation checks.
    """

    if dataset_path is None:
        dataset_path = DATASET_PATH

    repository_root = dataset_path.parent.parent.resolve()


    result = ValidationResult(
        name="Dataset Validator",
        passed=True,
    )

    try:
        projects = _load_projects(dataset_path)

    except FileNotFoundError:

        result.passed = False
        result.errors.append(
            f"Dataset not found: {dataset_path}"
        )
        return result

    except json.JSONDecodeError as exc:

        result.passed = False
        result.errors.append(
            f"Invalid JSON: {exc}"
        )
        return result

    duplicate_ids = _validate_duplicate_ids(projects)
    duplicate_titles = _validate_duplicate_titles(projects)
    missing_fields = _validate_required_fields(projects)
    empty_fields = _validate_empty_fields(projects)
    missing_files = _validate_starter_code(
        projects,
        repository_root,
    )

    result.details = {
        "projects": len(projects),
        "checks": {
            "duplicate_ids": duplicate_ids,
            "duplicate_titles": duplicate_titles,
            "missing_fields": missing_fields,
            "empty_fields": empty_fields,
            "missing_files": missing_files,
        },
    }

    result.errors.extend(duplicate_ids)
    result.errors.extend(duplicate_titles)
    result.errors.extend(missing_fields)
    result.errors.extend(empty_fields)

    # Starter code issues are warnings
    result.warnings.extend(missing_files)

    result.passed = not result.errors

    return result