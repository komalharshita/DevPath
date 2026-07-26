from dataclasses import dataclass, field
from typing import Any


@dataclass
class ValidationResult:
    """Represents the outcome of a validation check."""

    name: str
    passed: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    details: dict[str, Any] = field(default_factory=dict)