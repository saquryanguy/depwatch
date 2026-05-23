"""Build filtered severity reports using FilterCriteria."""

from __future__ import annotations

from typing import Dict, List, Optional

from depwatch.filter_engine import FilterCriteria, apply_filter
from depwatch.severity_classifier import classify_changes
from depwatch.severity_report import SeverityReport, build_severity_report


def build_filtered_report(
    package: str,
    old_version: str,
    new_version: str,
    lines: List[str],
    criteria: FilterCriteria,
) -> Optional[SeverityReport]:
    """Return a :class:`SeverityReport` for *package* after applying *criteria*.

    Returns *None* when the package is excluded by the package filter.
    Returns a report with no annotated lines when all lines are filtered out.
    """
    annotated = classify_changes(lines)
    filtered = apply_filter(package, lines, annotated, criteria)
    if filtered is None:
        return None

    # Re-classify only the surviving lines so counts are accurate.
    filtered_annotated = classify_changes(filtered)
    return build_severity_report(package, old_version, new_version, filtered)


def build_filtered_reports(
    packages: Dict[str, tuple],  # {package: (old_ver, new_ver, lines)}
    criteria: FilterCriteria,
) -> List[SeverityReport]:
    """Build filtered reports for multiple packages, skipping excluded ones.

    *packages* maps package name to a 3-tuple of
    ``(old_version, new_version, lines)``.
    """
    reports: List[SeverityReport] = []
    for pkg, (old_ver, new_ver, lines) in packages.items():
        report = build_filtered_report(pkg, old_ver, new_ver, lines, criteria)
        if report is not None:
            reports.append(report)
    return reports
