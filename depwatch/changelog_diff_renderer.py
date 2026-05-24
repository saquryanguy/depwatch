"""Renders changelog diffs into human-readable formats for display or export."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from depwatch.changelog_diff import ChangelogDiff
from depwatch.severity_classifier import Severity, highest_severity, classify_changes


@dataclass
class RenderedDiff:
    package: str
    old_version: str
    new_version: str
    severity: Severity
    lines: List[str]
    markdown: str
    plain: str


def _severity_badge(severity: Severity) -> str:
    badges = {
        Severity.CRITICAL: "🔴 CRITICAL",
        Severity.HIGH: "🟠 HIGH",
        Severity.MEDIUM: "🟡 MEDIUM",
        Severity.LOW: "🟢 LOW",
        Severity.SAFE: "✅ SAFE",
    }
    return badges.get(severity, "❓ UNKNOWN")


def _render_markdown(diff: ChangelogDiff, severity: Severity) -> str:
    lines = diff.lines or []
    badge = _severity_badge(severity)
    header = (
        f"### `{diff.package}` {diff.old_version} → {diff.new_version} "
        f"[{badge}]\n"
    )
    if not lines:
        return header + "_No changelog content found._\n"
    body = "\n".join(f"- {line}" for line in lines)
    return header + body + "\n"


def _render_plain(diff: ChangelogDiff, severity: Severity) -> str:
    lines = diff.lines or []
    badge = _severity_badge(severity)
    header = (
        f"{diff.package} {diff.old_version} -> {diff.new_version} [{badge}]\n"
        + "-" * 60 + "\n"
    )
    if not lines:
        return header + "  No changelog content found.\n"
    body = "\n".join(f"  * {line}" for line in lines)
    return header + body + "\n"


def render_diff(diff: ChangelogDiff) -> RenderedDiff:
    """Render a single ChangelogDiff into a RenderedDiff."""
    lines = diff.lines or []
    severity = highest_severity(classify_changes(lines))
    return RenderedDiff(
        package=diff.package,
        old_version=diff.old_version,
        new_version=diff.new_version,
        severity=severity,
        lines=lines,
        markdown=_render_markdown(diff, severity),
        plain=_render_plain(diff, severity),
    )


def render_diffs(
    diffs: List[ChangelogDiff],
    min_severity: Optional[Severity] = None,
) -> List[RenderedDiff]:
    """Render multiple diffs, optionally filtering by minimum severity."""
    rendered = [render_diff(d) for d in diffs]
    if min_severity is None:
        return rendered
    rank = {s: i for i, s in enumerate(reversed(list(Severity)))}
    threshold = rank.get(min_severity, 0)
    return [r for r in rendered if rank.get(r.severity, 0) >= threshold]
