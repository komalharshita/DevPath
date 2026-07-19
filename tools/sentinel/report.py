"""
Utilities for printing formatted Sentinel reports.
"""

from tools.sentinel.models import ValidationResult


ERROR_CHECKS = {
    "duplicate_ids",
    "duplicate_titles",
    "missing_fields",
    "empty_fields",
}

WARNING_CHECKS = {
    "missing_files",
}


def print_banner() -> None:
    """Print the Sentinel startup banner."""

    print("=" * 60)
    print("DevPath Sentinel")
    print("Repository Health & Integrity Validator")
    print("=" * 60)
    print()


def print_validation_result(result: ValidationResult) -> None:
    """Print a formatted validation report."""

    print(f"Running {result.name}...\n")

    print(f"Projects scanned : {result.details.get('projects', 0)}")
    print()

    checks = result.details.get("checks", {})

    check_order = (
        ("Duplicate IDs", "duplicate_ids"),
        ("Duplicate Titles", "duplicate_titles"),
        ("Required Fields", "missing_fields"),
        ("Empty Fields", "empty_fields"),
        ("Starter Code", "missing_files"),
    )

    passed_checks = 0

    for label, key in check_order:

        issues = checks.get(key, [])

        if not issues:
            print(f"✓ {label:.<28} PASS")
            passed_checks += 1
            continue

        if key in WARNING_CHECKS:
            print(f"⚠ {label:.<28} WARN ({len(issues)})")
        else:
            print(f"✗ {label:.<28} FAIL ({len(issues)})")

        for issue in issues:
            print(f"    • {issue}")

        print()

    print("=" * 60)

    print(f"Projects scanned : {result.details.get('projects', 0)}")
    print(f"Checks passed    : {passed_checks}")
    print(f"Warnings         : {len(result.warnings)}")
    print(f"Errors           : {len(result.errors)}")

    print()

    if result.errors:
        print("Status : FAILED")
    elif result.warnings:
        print("Status : PASSED WITH WARNINGS")
    else:
        print("Status : PASSED")

    print("=" * 60)