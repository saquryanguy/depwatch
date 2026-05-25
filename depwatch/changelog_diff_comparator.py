"""Compare two sets of changelog diffs to detect regressions or improvements."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from depwatch.changelog_diff import ChangelogDiff
from depwatch.severity_classifier import Severity, highest_severity, classify_changes


@dataclass
class ComparisonEntry:
    package: str
    old_severity: Severity
    new_severity: Severity
    added_lines: List[str]
    removed_lines: List[str]

    @property
    def regressed(self) -> bool:
        _rank = {Severity.SAFE: 0, Severity.LOW: 1, Severity.MEDIUM: 2,
                 Severity.HIGH: 3, Severity.CRITICAL: 4}
        return _rank[self.new_severity] > _rank[self.old_severity]

    @property
    def improved(self) -> bool:
        _rank = {Severity.SAFE: 0, Severity.LOW: 1, Severity.MEDIUM: 2,
                 Severity.HIGH: 3, Severity.CRITICAL: 4}
        return _rank[self.new_severity] < _rank[self.old_severity]


@dataclass
class ComparisonReport:
    entries: List[ComparisonEntry] = field(default_factory=list)
    packages_added: List[str] = field(default_factory=list)
    packages_removed: List[str] = field(default_factory=list)

    @property
    def regressions(self) -> List[ComparisonEntry]:
        return [e for e in self.entries if e.regressed]

    @property
    def improvements(self) -> List[ComparisonEntry]:
        return [e for e in self.entries if e.improved]


def _severity_for_diff(diff: ChangelogDiff) -> Severity:
    if not diff.lines:
        return Severity.SAFE
    return highest_severity(classify_changes(diff.lines))


def compare_diffs(
    old_diffs: List[ChangelogDiff],
    new_diffs: List[ChangelogDiff],
) -> ComparisonReport:
    old_map: Dict[str, ChangelogDiff] = {d.package: d for d in old_diffs}
    new_map: Dict[str, ChangelogDiff] = {d.package: d for d in new_diffs}

    entries: List[ComparisonEntry] = []
    for package, new_diff in new_map.items():
        if package not in old_map:
            continue
        old_diff = old_map[package]
        old_lines = set(old_diff.lines or [])
        new_lines = set(new_diff.lines or [])
        entry = ComparisonEntry(
            package=package,
            old_severity=_severity_for_diff(old_diff),
            new_severity=_severity_for_diff(new_diff),
            added_lines=sorted(new_lines - old_lines),
            removed_lines=sorted(old_lines - new_lines),
        )
        entries.append(entry)

    added = [p for p in new_map if p not in old_map]
    removed = [p for p in old_map if p not in new_map]
    return ComparisonReport(entries=entries, packages_added=added, packages_removed=removed)
