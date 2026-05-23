"""Filter engine for narrowing down breaking changes by severity, package, or keyword."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from depwatch.severity_classifier import Severity


@dataclass
class FilterCriteria:
    """Criteria used to filter breaking-change reports."""

    min_severity: Severity = Severity.LOW
    packages: List[str] = field(default_factory=list)  # empty = all packages
    keywords: List[str] = field(default_factory=list)  # empty = no keyword filter


def _severity_rank(severity: Severity) -> int:
    """Return a numeric rank so severities can be compared."""
    order = [Severity.LOW, Severity.MEDIUM, Severity.HIGH, Severity.CRITICAL]
    return order.index(severity)


def matches_severity(severity: Severity, min_severity: Severity) -> bool:
    """Return True when *severity* is at least *min_severity*."""
    return _severity_rank(severity) >= _severity_rank(min_severity)


def matches_package(package: str, allowed: List[str]) -> bool:
    """Return True when *package* is in *allowed* (case-insensitive), or *allowed* is empty."""
    if not allowed:
        return True
    normalized = [p.lower().replace("-", "_") for p in allowed]
    return package.lower().replace("-", "_") in normalized


def matches_keywords(line: str, keywords: List[str]) -> bool:
    """Return True when *line* contains at least one keyword (case-insensitive), or no keywords given."""
    if not keywords:
        return True
    lower = line.lower()
    return any(kw.lower() in lower for kw in keywords)


def filter_lines(
    lines: List[str],
    annotated: List[tuple],  # list of (line, Severity)
    criteria: FilterCriteria,
) -> List[str]:
    """Return only those *lines* whose paired severity and content pass *criteria*.

    *annotated* must be parallel to *lines* (same length, same order).
    """
    if len(lines) != len(annotated):
        raise ValueError("lines and annotated must have the same length")

    result = []
    for line, (_, severity) in zip(lines, annotated):
        if not matches_severity(severity, criteria.min_severity):
            continue
        if not matches_keywords(line, criteria.keywords):
            continue
        result.append(line)
    return result


def apply_filter(
    package: str,
    lines: List[str],
    annotated: List[tuple],
    criteria: FilterCriteria,
) -> Optional[List[str]]:
    """Return filtered lines for *package*, or None if the package is excluded by criteria."""
    if not matches_package(package, criteria.packages):
        return None
    return filter_lines(lines, annotated, criteria)
