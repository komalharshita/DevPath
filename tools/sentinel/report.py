"""
Utilities for printing formatted Sentinel reports.
"""


def print_banner() -> None:
    """Print the Sentinel startup banner."""

    print("=" * 50)
    print("DevPath Sentinel")
    print("Repository Health & Integrity Validator")
    print("=" * 50)
    print()


def print_no_validators() -> None:
    """Print the default message when no validators are registered."""

    print("No validators registered yet.")