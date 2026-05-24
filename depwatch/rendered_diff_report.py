"""Aggregates rendered diffs into a single report structure."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from depwatch.changelog_diff import ChangelogDiff
from depwatch.changelog_diff_renderer import RenderedDiff, render_diffs
from depwatch.diff_render_config import DiffRenderConfig
from depwatch.severity_classifier import Severity


@dataclass
class RenderedDiffReport:
    entries: List[RenderedDiff] = field(default_factory=list)
    total_packages: int = 0
    risky_packages: int = 0
    highest_severity: Severity = Severity.SAFE

    def is_clean(self) -> bool:
        return self.highest_severity == Severity.SAFE


def _highest_from_entries(entries: List[RenderedDiff]) -> Severity:
    rank = list(reversed(list(Severity)))
    order = {s: i for i, s in enumerate(rank)}
    best = Severity.SAFE
    best_rank = 0
    for entry in entries:
        r = order.get(entry.severity, 0)
        if r > best_rank:
            best_rank = r
            best = entry.severity
    return best


def build_rendered_diff_report(
    diffs: List[ChangelogDiff],
    config: Optional[DiffRenderConfig] = None,
) -> RenderedDiffReport:
    if config is None:
        config = DiffRenderConfig()

    min_sev = None if config.include_safe else Severity.LOW
    if config.min_severity is not None:
        min_sev = config.min_severity

    entries = render_diffs(diffs, min_severity=min_sev)

    # Truncate lines per package
    for entry in entries:
        if len(entry.lines) > config.max_lines_per_package:
            entry.lines = entry.lines[: config.max_lines_per_package]

    risky = sum(1 for e in entries if e.severity != Severity.SAFE)
    highest = _highest_from_entries(entries)

    return RenderedDiffReport(
        entries=entries,
        total_packages=len(entries),
        risky_packages=risky,
        highest_severity=highest,
    )


def format_rendered_diff_report(
    report: RenderedDiffReport,
    output_format: str = "markdown",
) -> str:
    if not report.entries:
        return "No dependency changes detected.\n"
    parts = []
    for entry in report.entries:
        if output_format == "plain":
            parts.append(entry.plain)
        else:
            parts.append(entry.markdown)
    return "\n".join(parts)
