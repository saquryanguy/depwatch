"""Summarizes a collection of changelog diffs into a concise report."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from depwatch.changelog_diff import ChangelogDiff
from depwatch.severity_classifier import Severity, highest_severity, classify_changes


@dataclass
class DiffSummaryEntry:
    package: str
    old_version: str
    new_version: str
    total_lines: int
    breaking_count: int
    highest_severity: Severity
    headline: Optional[str] = None

    @property
    def is_safe(self) -> bool:
        return self.breaking_count == 0


@dataclass
class DiffSummaryReport:
    entries: List[DiffSummaryEntry] = field(default_factory=list)
    total_packages: int = 0
    affected_packages: int = 0
    overall_severity: Severity = Severity.SAFE


def _pick_headline(lines: List[str]) -> Optional[str]:
    for line in lines:
        stripped = line.strip().lstrip("#- *")
        if len(stripped) > 10:
            return stripped[:120]
    return None


def summarize_diff(diff: ChangelogDiff) -> DiffSummaryEntry:
    lines = diff.lines if diff.lines else []
    classified = classify_changes(lines)
    sev = highest_severity(classified)
    breaking = sum(1 for s in classified if s != Severity.SAFE)
    return DiffSummaryEntry(
        package=diff.package,
        old_version=diff.old_version,
        new_version=diff.new_version,
        total_lines=len(lines),
        breaking_count=breaking,
        highest_severity=sev,
        headline=_pick_headline(lines),
    )


def build_diff_summary_report(diffs: List[ChangelogDiff]) -> DiffSummaryReport:
    entries = [summarize_diff(d) for d in diffs]
    affected = [e for e in entries if not e.is_safe]
    severities = [e.highest_severity for e in entries] or [Severity.SAFE]
    overall = highest_severity(severities)
    return DiffSummaryReport(
        entries=entries,
        total_packages=len(entries),
        affected_packages=len(affected),
        overall_severity=overall,
    )


def format_diff_summary_report(report: DiffSummaryReport) -> str:
    if not report.entries:
        return "## Dependency Summary\n\nNo dependency changes detected."
    lines = ["## Dependency Summary", ""]
    lines.append(f"- **Packages checked:** {report.total_packages}")
    lines.append(f"- **Packages with changes:** {report.affected_packages}")
    lines.append(f"- **Overall severity:** {report.overall_severity.name}")
    lines.append("")
    for entry in report.entries:
        icon = "✅" if entry.is_safe else "⚠️"
        lines.append(f"{icon} **{entry.package}** `{entry.old_version}` → `{entry.new_version}`")
        if entry.headline:
            lines.append(f"   > {entry.headline}")
    return "\n".join(lines)
