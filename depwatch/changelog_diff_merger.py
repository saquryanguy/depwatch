"""Merge multiple ChangelogDiff objects into a unified summary per package."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from depwatch.changelog_diff import ChangelogDiff
from depwatch.severity_classifier import Severity, highest_severity, classify_changes


@dataclass
class MergedDiff:
    """A single package's changelog lines merged across multiple diffs."""

    package: str
    from_version: Optional[str]
    to_version: Optional[str]
    lines: List[str]
    severity: Severity

    @property
    def is_empty(self) -> bool:
        return not self.lines


@dataclass
class MergedDiffReport:
    """Collection of merged diffs, keyed by package name."""

    entries: Dict[str, MergedDiff] = field(default_factory=dict)

    @property
    def packages(self) -> List[str]:
        return list(self.entries.keys())

    @property
    def total(self) -> int:
        return len(self.entries)

    @property
    def has_breaking(self) -> bool:
        return any(
            e.severity not in (Severity.SAFE,)
            for e in self.entries.values()
        )


def merge_diffs(diffs: List[ChangelogDiff]) -> MergedDiffReport:
    """Merge a list of ChangelogDiff objects into a MergedDiffReport.

    When multiple diffs exist for the same package the lines are concatenated
    and the earliest from_version / latest to_version are kept.
    """
    grouped: Dict[str, List[ChangelogDiff]] = {}
    for diff in diffs:
        if diff.package not in grouped:
            grouped[diff.package] = []
        grouped[diff.package].append(diff)

    entries: Dict[str, MergedDiff] = {}
    for package, pkg_diffs in grouped.items():
        all_lines: List[str] = []
        from_versions = [d.from_version for d in pkg_diffs if d.from_version]
        to_versions = [d.to_version for d in pkg_diffs if d.to_version]
        for d in pkg_diffs:
            all_lines.extend(d.lines or [])

        severity = highest_severity(classify_changes(all_lines))
        entries[package] = MergedDiff(
            package=package,
            from_version=from_versions[0] if from_versions else None,
            to_version=to_versions[-1] if to_versions else None,
            lines=all_lines,
            severity=severity,
        )

    return MergedDiffReport(entries=entries)
