"""Applies DiffSummaryConfig filtering to a DiffSummaryReport."""
from __future__ import annotations

from typing import List, Optional

from depwatch.changelog_diff_summarizer import (
    DiffSummaryEntry,
    DiffSummaryReport,
    build_diff_summary_report,
)
from depwatch.changelog_diff import ChangelogDiff
from depwatch.diff_summary_config import DiffSummaryConfig
from depwatch.severity_classifier import Severity, highest_severity

_SEVERITY_RANK = {
    Severity.SAFE: 0,
    Severity.LOW: 1,
    Severity.MEDIUM: 2,
    Severity.HIGH: 3,
    Severity.CRITICAL: 4,
}


def _rank(sev: Severity) -> int:
    return _SEVERITY_RANK.get(sev, 0)


def _entry_meets_config(entry: DiffSummaryEntry, config: DiffSummaryConfig) -> bool:
    if config.only_packages and entry.package not in config.only_packages:
        return False
    if not config.include_safe and entry.is_safe:
        return False
    if config.min_severity is not None:
        if _rank(entry.highest_severity) < _rank(config.min_severity):
            return False
    return True


def filter_diff_summary(
    report: DiffSummaryReport,
    config: Optional[DiffSummaryConfig] = None,
) -> DiffSummaryReport:
    if config is None:
        return report

    filtered = [e for e in report.entries if _entry_meets_config(e, config)]
    affected = [e for e in filtered if not e.is_safe]
    severities = [e.highest_severity for e in filtered] or [Severity.SAFE]
    overall = highest_severity(severities)

    return DiffSummaryReport(
        entries=filtered,
        total_packages=len(filtered),
        affected_packages=len(affected),
        overall_severity=overall,
    )


def build_filtered_diff_summary(
    diffs: List[ChangelogDiff],
    config: Optional[DiffSummaryConfig] = None,
) -> DiffSummaryReport:
    report = build_diff_summary_report(diffs)
    return filter_diff_summary(report, config)
