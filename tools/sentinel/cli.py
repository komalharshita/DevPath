"""
Command-line entry point for DevPath Sentinel.
"""

from __future__ import annotations

import sys

from .report import print_banner, print_validation_result
from .validators import dataset_validator, starter_code_validator


def main() -> None:
    """Run DevPath Sentinel."""

    print_banner()

    validators = [
        dataset_validator.run,
        starter_code_validator.run,
    ]

    has_errors = False

    for validator in validators:
        result = validator()

        print_validation_result(result)

        if result.errors:
            has_errors = True

    sys.exit(1 if has_errors else 0)


if __name__ == "__main__":
    main()
