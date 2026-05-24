"""Annotates changelog lines with severity and category metadata."""

from dataclasses import dataclass, field
from typing import List, Optional

from depwatch.severity_classifier import Severity, classify_line


CATEGORY_KEYWORDS = {
    "security": ["cve", "security", "vulnerability", "exploit", "patch"],
    "api": ["api", "interface", "signature", "endpoint", "parameter"],
    "performance": ["performance", "speed", "memory", "latency", "throughput"],
    "behaviour": ["behaviour", "behavior", "default", "changed", "now returns"],
}


@dataclass
class AnnotatedLine:
    text: str
    severity: Severity
    categories: List[str] = field(default_factory=list)
    line_number: Optional[int] = None


def detect_categories(line: str) -> List[str]:
    """Return list of matching category labels for a changelog line."""
    lower = line.lower()
    return [
        category
        for category, keywords in CATEGORY_KEYWORDS.items()
        if any(kw in lower for kw in keywords)
    ]


def annotate_line(text: str, line_number: Optional[int] = None) -> AnnotatedLine:
    """Annotate a single changelog line with severity and categories."""
    severity = classify_line(text)
    categories = detect_categories(text)
    return AnnotatedLine(
        text=text,
        severity=severity,
        categories=categories,
        line_number=line_number,
    )


def annotate_lines(lines: List[str]) -> List[AnnotatedLine]:
    """Annotate a list of changelog lines, preserving order and line numbers."""
    return [
        annotate_line(text, line_number=idx + 1)
        for idx, text in enumerate(lines)
    ]


def filter_annotated(
    annotated: List[AnnotatedLine],
    min_severity: Severity = Severity.LOW,
    categories: Optional[List[str]] = None,
) -> List[AnnotatedLine]:
    """Filter annotated lines by minimum severity and optional category list."""
    severity_order = [Severity.LOW, Severity.MEDIUM, Severity.HIGH, Severity.CRITICAL]
    min_rank = severity_order.index(min_severity)

    result = [
        al for al in annotated
        if severity_order.index(al.severity) >= min_rank
    ]

    if categories:
        allowed = set(categories)
        result = [al for al in result if set(al.categories) & allowed]

    return result
