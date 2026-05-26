"""Filter a TaggerReport based on TaggerConfig criteria."""
from __future__ import annotations

from typing import List, Optional

from depwatch.changelog_diff_tagger import TaggedDiff, TaggerReport
from depwatch.severity_classifier import Severity
from depwatch.tagger_config import TaggerConfig

_SEVERITY_RANK = {
    Severity.SAFE: 0,
    Severity.LOW: 1,
    Severity.MEDIUM: 2,
    Severity.HIGH: 3,
    Severity.CRITICAL: 4,
}


def _meets_min_severity(entry: TaggedDiff, min_severity: Optional[Severity]) -> bool:
    if min_severity is None:
        return True
    return _SEVERITY_RANK.get(entry.severity, 0) >= _SEVERITY_RANK.get(min_severity, 0)


def filter_tagged_report(
    report: TaggerReport, config: TaggerConfig
) -> TaggerReport:
    entries: List[TaggedDiff] = []
    for entry in report.entries:
        if config.skip_safe and entry.severity == Severity.SAFE:
            continue
        if not _meets_min_severity(entry, config.min_severity):
            continue
        entries.append(entry)
    return TaggerReport(entries=entries)


def format_tagged_report_markdown(report: TaggerReport) -> str:
    if not report.entries:
        return "_No tagged diffs._"
    lines = ["## Tagged Changelog Diffs", ""]
    for entry in report.entries:
        tag_str = ", ".join(f"`{t}`" for t in entry.tags) if entry.tags else "_none_"
        lines.append(f"### {entry.package}")
        lines.append(f"- **Severity:** {entry.severity.value}")
        lines.append(f"- **Tags:** {tag_str}")
        lines.append("")
    return "\n".join(lines)
