"""
Command-line entry point for DevPath Sentinel.
"""

if __package__:
    # Running as: python -m tools.sentinel.cli
    from .report import print_banner, print_no_validators
else:
    # Running as: python tools/sentinel/cli.py
    from report import print_banner, print_no_validators


def main() -> None:
    """Run DevPath Sentinel."""

    print_banner()
    print_no_validators()


if __name__ == "__main__":
    main()