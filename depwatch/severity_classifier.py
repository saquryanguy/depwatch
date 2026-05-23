"""Classifies breaking changes by severity level."""

from enum import Enum
from typing import List, Tuple


class Severity(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    SAFE = "safe"


_CRITICAL_PATTERNS = [
    "removed",
    "dropped support",
    "no longer supported",
    "breaking change",
    "incompatible",
]

_HIGH_PATTERNS = [
    "deprecated",
    "renamed",
    "moved",
    "replaced",
]

_MEDIUM_PATTERNS = [
    "changed behavior",
    "changed default",
    "now raises",
    "raises an error",
]

_LOW_PATTERNS = [
    "warning",
    "note:",
    "minor",
]


def classify_line(line: str) -> Severity:
    """Return the severity of a single changelog line."""
    lower = line.lower()
    for pattern in _CRITICAL_PATTERNS:
        if pattern in lower:
            return Severity.CRITICAL
    for pattern in _HIGH_PATTERNS:
        if pattern in lower:
            return Severity.HIGH
    for pattern in _MEDIUM_PATTERNS:
        if pattern in lower:
            return Severity.MEDIUM
    for pattern in _LOW_PATTERNS:
        if pattern in lower:
            return Severity.LOW
    return Severity.SAFE


def classify_changes(lines: List[str]) -> List[Tuple[str, Severity]]:
    """Return a list of (line, severity) pairs for each line."""
    return [(line, classify_line(line)) for line in lines if line.strip()]


def highest_severity(lines: List[str]) -> Severity:
    """Return the most severe classification across all lines."""
    order = [Severity.CRITICAL, Severity.HIGH, Severity.MEDIUM, Severity.LOW, Severity.SAFE]
    classified = [classify_line(line) for line in lines if line.strip()]
    if not classified:
        return Severity.SAFE
    for level in order:
        if level in classified:
            return level
    return Severity.SAFE
