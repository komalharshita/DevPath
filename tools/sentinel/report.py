"""
Console report utilities for DevPath Sentinel.
"""

from __future__ import annotations

from tools.sentinel.models import ValidationResult


_STATUS = {
    True: "PASS",
    False: "FAIL",
}

_SEVERITY_ICON = {
    "error": "✗",
    "warning": "!",
}


def print_banner() -> None:
    """Print the DevPath Sentinel banner."""

    print("=" * 60)
    print("DevPath Sentinel")
    print("=" * 60)


def print_validation_result(result: ValidationResult) -> None:
    """
    Print a formatted validation report.
    """

    _print_header(result)
    _print_resource_summary(result)
    _print_checks(result)
    _print_messages(result)


def _print_header(result: ValidationResult) -> None:
    """
    Print report header.
    """

    print(f"\n=== {result.name} ===")
    print(f"Status : {_STATUS[result.passed]}")


def _print_resource_summary(result: ValidationResult) -> None:
    """
    Print resource summary.
    """

    details = result.details

    resource = details.get("resource")
    count = details.get("count")

    if resource is not None and count is not None:
        print(f"{resource}: {count}")


def _print_checks(result: ValidationResult) -> None:
    """
    Print validation checks.
    """

    details = result.details

    checks = details.get("checks", {})
    metadata = details.get("metadata", {})

    if not checks:
        return

    print("\nChecks")

    for check_name, issues in checks.items():
        info = metadata.get(check_name, {})

        label = info.get("label", check_name.replace("_", " ").title())
        severity = info.get("severity", "error")

        icon = _SEVERITY_ICON.get(severity, "-")

        print(f"  {icon} {label:<24} {len(issues)} issue(s)")


def _print_messages(result: ValidationResult) -> None:
    """
    Print detailed errors and warnings.
    """

    if result.errors:
        print("\nErrors")

        for message in result.errors:
            print(f"  - {message}")

    if result.warnings:
        print("\nWarnings")

        for message in result.warnings:
            print(f"  - {message}")
