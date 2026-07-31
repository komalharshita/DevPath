"""
Starter Code Integrity Validator

This validator inspects the repository's ``starter_code/`` directory and
checks its overall integrity.

Responsibilities:
- Detect orphan starter code files.
- Detect empty starter code files.
- Detect unsupported file types.
- Detect hidden files.

The validator returns a ValidationResult and performs no console output.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from tools.sentinel.models import ValidationResult

REPO_ROOT = Path(__file__).resolve().parents[3]
DATASET_PATH = REPO_ROOT / "data" / "projects.json"
STARTER_CODE_DIR = REPO_ROOT / "starter_code"

ALLOWED_STARTER_CODE_EXTENSIONS = {
    ".py",
    ".js",
    ".java",
    ".html",
    ".css",
    ".yml",
    ".yaml",
    ".txt",
    ".md",
}


def _load_projects(dataset_path: Path) -> list[dict[str, Any]]:
    """
    Load the project dataset.

    Args:
        dataset_path: Path to the projects.json dataset.

    Returns:
        A list of project dictionaries.

    Raises:
        FileNotFoundError:
            If the dataset file does not exist.

        ValueError:
            If the dataset is not a valid JSON array.
    """
    if not dataset_path.is_file():
        raise FileNotFoundError(f"Dataset file not found: {dataset_path}")

    try:
        with dataset_path.open("r", encoding="utf-8") as file:
            projects = json.load(file)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON in dataset: {dataset_path}") from exc

    if not isinstance(projects, list):
        raise ValueError("Dataset must contain a JSON array of projects.")

    return projects


def _collect_referenced_files(
    projects: list[dict[str, Any]],
) -> set[Path]:
    """
    Collect all starter code files referenced by the dataset.

    Args:
        projects: List of project dictionaries loaded from the dataset.

    Returns:
        A set of repository-relative starter code paths.
    """
    referenced_files: set[Path] = set()

    for project in projects:
        starter_code = project.get("starter_code")

        if not isinstance(starter_code, str):
            continue

        starter_code = starter_code.strip()

        if not starter_code:
            continue

        referenced_files.add(Path(starter_code))

    return referenced_files


def _collect_repository_files(
    starter_code_dir: Path,
) -> list[Path]:
    """
    Collect every file inside the starter_code directory.

    Args:
        starter_code_dir: Path to the repository's starter_code directory.

    Returns:
        A list of repository-relative starter code file paths.

    Raises:
        FileNotFoundError:
            If the starter_code directory does not exist.

        NotADirectoryError:
            If the provided path is not a directory.
    """
    if not starter_code_dir.exists():
        raise FileNotFoundError(f"Starter code directory not found: {starter_code_dir}")

    if not starter_code_dir.is_dir():
        raise NotADirectoryError(f"Expected a directory: {starter_code_dir}")

    repository_files: list[Path] = []

    for path in sorted(starter_code_dir.rglob("*")):
        if path.is_file():
            repository_files.append(
                Path("starter_code") / path.relative_to(starter_code_dir)
            )

    return repository_files


def _validate_orphan_files(
    repository_files: list[Path],
    referenced_files: set[Path],
) -> list[str]:
    """
    Detect starter code files that are not referenced by the dataset.

    Args:
        repository_files: Repository-relative paths of all files present
            in the starter_code directory.
        referenced_files: Repository-relative paths referenced by the
            project dataset.

    Returns:
        A sorted list of orphan starter code file paths.
    """
    orphan_files = [
        str(file_path)
        for file_path in repository_files
        if file_path not in referenced_files
    ]

    return sorted(orphan_files)


def _validate_empty_files(
    repository_files: list[Path],
    starter_code_dir: Path,
) -> list[str]:
    """
    Detect empty starter code files.

    Args:
        repository_files: Repository-relative paths of all files present
            in the starter_code directory.

    Returns:
        A sorted list of empty starter code file paths.
    """
    empty_files: list[str] = []

    for file_path in repository_files:
        absolute_path = starter_code_dir / file_path.relative_to("starter_code")

        if absolute_path.stat().st_size == 0:
            empty_files.append(str(file_path))

    return sorted(empty_files)


def _validate_hidden_files(
    repository_files: list[Path],
) -> list[str]:
    """
    Detect hidden files inside the starter_code directory.

    Args:
        repository_files: Repository-relative paths of all files present
            in the starter_code directory.

    Returns:
        A sorted list of hidden starter code file paths.
    """
    hidden_files = [
        str(file_path)
        for file_path in repository_files
        if file_path.name.startswith(".")
    ]

    return sorted(hidden_files)


def _validate_supported_extensions(
    repository_files: list[Path],
) -> list[str]:
    """
    Detect starter code files with unsupported file extensions.

    Args:
        repository_files: Repository-relative paths of all files present
            in the starter_code directory.

    Returns:
        A sorted list of starter code file paths that use unsupported
        file extensions.
    """
    unsupported_files = [
        str(file_path)
        for file_path in repository_files
        if file_path.suffix.lower() not in ALLOWED_STARTER_CODE_EXTENSIONS
    ]

    return sorted(unsupported_files)


def run(
    dataset_path: Path | None = None,
    starter_code_dir: Path | None = None,
) -> ValidationResult:
    """
    Execute the Starter Code Integrity Validator.

    Args:
        dataset_path: Optional path to the projects dataset.
        starter_code_dir: Optional path to the starter_code directory.

    Returns:
        ValidationResult describing the validation outcome.
    """
    dataset_path = dataset_path or DATASET_PATH
    starter_code_dir = starter_code_dir or STARTER_CODE_DIR

    try:
        projects = _load_projects(dataset_path)

        referenced_files = _collect_referenced_files(projects)
        repository_files = _collect_repository_files(starter_code_dir)

        orphan_files = _validate_orphan_files(
            repository_files,
            referenced_files,
        )
        empty_files = _validate_empty_files(
            repository_files,
            starter_code_dir,
        )
        hidden_files = _validate_hidden_files(repository_files)
        unsupported_files = _validate_supported_extensions(
            repository_files,
        )

    except (
        FileNotFoundError,
        NotADirectoryError,
        ValueError,
    ) as exc:
        return ValidationResult(
            name="Starter Code Integrity Validator",
            passed=False,
            errors=[str(exc)],
            warnings=[],
            details={},
        )

    errors: list[str] = []

    if orphan_files:
        errors.append(f"Orphan Files: {len(orphan_files)} issue(s) detected.")

    if empty_files:
        errors.append(f"Empty Files: {len(empty_files)} issue(s) detected.")

    warnings: list[str] = []

    if hidden_files:
        warnings.append(f"Hidden Files: {len(hidden_files)} issue(s) detected.")

    if unsupported_files:
        warnings.append(
            f"Unsupported Extensions: {len(unsupported_files)} issue(s) detected."
        )

    passed = not errors

    return ValidationResult(
        name="Starter Code Integrity Validator",
        passed=passed,
        errors=errors,
        warnings=warnings,
        details={
            "resource": "Starter Code Files",
            "count": len(repository_files),
            "checks": {
                "orphan_files": orphan_files,
                "empty_files": empty_files,
                "hidden_files": hidden_files,
                "unsupported_extensions": unsupported_files,
            },
            "metadata": {
                "orphan_files": {
                    "label": "Orphan Files",
                    "severity": "error",
                },
                "empty_files": {
                    "label": "Empty Files",
                    "severity": "error",
                },
                "hidden_files": {
                    "label": "Hidden Files",
                    "severity": "warning",
                },
                "unsupported_extensions": {
                    "label": "Unsupported Extensions",
                    "severity": "warning",
                },
            },
        },
    )
