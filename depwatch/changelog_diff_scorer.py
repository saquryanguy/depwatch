"""Combines changelog diff and scoring into a unified ranked report."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from depwatch.changelog_diff import ChangelogDiff
from depwatch.changelog_scorer import ChangelogScore, score_changelog_diff
from depwatch.severity_classifier import Severity, highest_severity, classify_changes


@dataclass
class DiffScoreEntry:
    """Pairs a ChangelogDiff with its computed ChangelogScore."""

    diff: ChangelogDiff
    score: ChangelogScore

    @property
    def package(self) -> str:
        return self.diff.package

    @property
    def risk_label(self) -> str:
        return self.score.risk_label

    @property
    def is_risky(self) -> bool:
        return self.score.risk_score > 0


@dataclass
class DiffScoreReport:
    """Ranked collection of DiffScoreEntry items."""

    entries: List[DiffScoreEntry] = field(default_factory=list)
    overall_severity: Severity = Severity.SAFE

    @property
    def total(self) -> int:
        return len(self.entries)

    @property
    def risky_count(self) -> int:
        return sum(1 for e in self.entries if e.is_risky)


def build_diff_score_report(diffs: List[ChangelogDiff]) -> DiffScoreReport:
    """Score each diff and assemble a ranked DiffScoreReport."""
    entries: List[DiffScoreEntry] = []
    severities: List[Severity] = []

    for diff in diffs:
        score = score_changelog_diff(diff)
        entries.append(DiffScoreEntry(diff=diff, score=score))
        if diff.lines:
            severities.append(highest_severity(classify_changes(diff.lines)))

    entries.sort(key=lambda e: e.score.risk_score, reverse=True)
    overall = highest_severity(severities) if severities else Severity.SAFE

    return DiffScoreReport(entries=entries, overall_severity=overall)


def format_diff_score_report(report: DiffScoreReport) -> str:
    """Return a markdown string summarising the DiffScoreReport."""
    if not report.entries:
        return "## Changelog Diff Score Report\n\nNo dependency upgrades analysed.\n"

    lines = [
        "## Changelog Diff Score Report\n",
        f"**Overall severity:** {report.overall_severity.value}  ",
        f"**Packages analysed:** {report.total}  ",
        f"**Risky upgrades:** {report.risky_count}\n",
        "| Package | From | To | Risk | Score |",
        "| --- | --- | --- | --- | --- |",
    ]
    for entry in report.entries:
        d = entry.diff
        lines.append(
            f"| {d.package} | {d.old_version or '—'} | {d.new_version or '—'} "
            f"| {entry.risk_label} | {entry.score.risk_score} |"
        )
    return "\n".join(lines) + "\n"
