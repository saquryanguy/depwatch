"""Apply ComparatorConfig filters to a ComparisonReport."""
from __future__ import annotations

from typing import List

from depwatch.changelog_diff_comparator import ComparisonEntry, ComparisonReport
from depwatch.comparator_config import ComparatorConfig
from depwatch.severity_classifier import Severity

_RANK: dict = {
    Severity.SAFE: 0,
    Severity.LOW: 1,
    Severity.MEDIUM: 2,
    Severity.HIGH: 3,
    Severity.CRITICAL: 4,
}


def _meets_min_severity(entry: ComparisonEntry, min_sev: Severity) -> bool:
    return _RANK[entry.new_severity] >= _RANK[min_sev]


def filter_comparison(
    report: ComparisonReport,
    config: ComparatorConfig,
) -> ComparisonReport:
    entries: List[ComparisonEntry] = []
    for entry in report.entries:
        if entry.package in config.ignore_packages:
            continue
        if config.only_regressions and not entry.regressed:
            continue
        if config.min_severity is not None and not _meets_min_severity(entry, config.min_severity):
            continue
        entries.append(entry)

    added = [p for p in report.packages_added if p not in config.ignore_packages]
    removed = [p for p in report.packages_removed if p not in config.ignore_packages]
    return ComparisonReport(entries=entries, packages_added=added, packages_removed=removed)


def format_comparison_markdown(report: ComparisonReport) -> str:
    lines: List[str] = ["## Changelog Diff Comparison\n"]
    if not report.entries and not report.packages_added and not report.packages_removed:
        lines.append("_No changes detected._")
        return "\n".join(lines)
    if report.regressions:
        lines.append("### ⚠️ Regressions")
        for e in report.regressions:
            lines.append(f"- **{e.package}**: {e.old_severity.name} → {e.new_severity.name}")
    if report.improvements:
        lines.append("### ✅ Improvements")
        for e in report.improvements:
            lines.append(f"- **{e.package}**: {e.old_severity.name} → {e.new_severity.name}")
    if report.packages_added:
        lines.append("### ➕ New packages")
        for p in report.packages_added:
            lines.append(f"- {p}")
    if report.packages_removed:
        lines.append("### ➖ Removed packages")
        for p in report.packages_removed:
            lines.append(f"- {p}")
    return "\n".join(lines)
