"""
Command-line entry point for DevPath Sentinel.
"""
import sys

from .report import print_banner, print_validation_result
from .validators.dataset_validator import run


def main() -> None:
    """Run DevPath Sentinel."""

    print_banner()

    result = run()

    print_validation_result(result)

    if result.errors:
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()