"""Groups changelog diffs by severity and package for structured reporting."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from depwatch.changelog_diff import ChangelogDiff
from depwatch.severity_classifier import Severity, classify_changes, highest_severity


@dataclass
class DiffGroup:
    severity: Severity
    diffs: List[ChangelogDiff] = field(default_factory=list)

    @property
    def packages(self) -> List[str]:
        return [d.package for d in self.diffs]

    @property
    def count(self) -> int:
        return len(self.diffs)


@dataclass
class GroupedDiffReport:
    groups: Dict[str, DiffGroup] = field(default_factory=dict)

    @property
    def total(self) -> int:
        return sum(g.count for g in self.groups.values())

    @property
    def severity_names(self) -> List[str]:
        return list(self.groups.keys())

    def get(self, severity: Severity) -> DiffGroup:
        return self.groups.get(severity.name, DiffGroup(severity=severity))


def _severity_for_diff(diff: ChangelogDiff) -> Severity:
    lines = diff.lines if diff.lines else []
    classified = classify_changes(lines)
    return highest_severity(classified)


def group_diffs_by_severity(diffs: List[ChangelogDiff]) -> GroupedDiffReport:
    """Group a list of ChangelogDiff objects by their highest severity."""
    groups: Dict[str, DiffGroup] = {}

    for diff in diffs:
        sev = _severity_for_diff(diff)
        key = sev.name
        if key not in groups:
            groups[key] = DiffGroup(severity=sev)
        groups[key].diffs.append(diff)

    # Sort by severity descending (CRITICAL first)
    order = [s.name for s in reversed(list(Severity))]
    sorted_groups = {k: groups[k] for k in order if k in groups}

    return GroupedDiffReport(groups=sorted_groups)
