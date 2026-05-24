"""Summarizes changelog sections into structured human-readable output."""

from dataclasses import dataclass, field
from typing import List, Optional

from depwatch.severity_classifier import Severity, classify_changes, highest_severity


@dataclass
class ChangelogSummary:
    package: str
    from_version: str
    to_version: str
    total_lines: int
    breaking_count: int
    highest_severity: Severity
    headline: str
    bullet_points: List[str] = field(default_factory=list)


def _pick_headline(package: str, from_version: str, to_version: str, severity: Severity) -> str:
    """Build a one-line headline for the summary."""
    label = severity.value.upper()
    return f"[{label}] {package}: {from_version} → {to_version}"


def _extract_bullet_points(lines: List[str], max_bullets: int = 5) -> List[str]:
    """Return up to *max_bullets* non-empty lines as bullet points."""
    bullets: List[str] = []
    for line in lines:
        stripped = line.strip().lstrip("-* ").strip()
        if stripped:
            bullets.append(stripped)
        if len(bullets) >= max_bullets:
            break
    return bullets


def build_changelog_summary(
    package: str,
    from_version: str,
    to_version: str,
    lines: List[str],
    max_bullets: int = 5,
) -> ChangelogSummary:
    """Build a ChangelogSummary from a list of changelog lines."""
    annotated = classify_changes(lines)
    breaking = [a for a in annotated if a.severity in (Severity.CRITICAL, Severity.HIGH)]
    severity = highest_severity(annotated)
    headline = _pick_headline(package, from_version, to_version, severity)
    bullets = _extract_bullet_points(lines, max_bullets=max_bullets)
    return ChangelogSummary(
        package=package,
        from_version=from_version,
        to_version=to_version,
        total_lines=len(lines),
        breaking_count=len(breaking),
        highest_severity=severity,
        headline=headline,
        bullet_points=bullets,
    )


def format_changelog_summary(summary: ChangelogSummary) -> str:
    """Render a ChangelogSummary as a Markdown snippet."""
    lines = [f"### {summary.headline}"]
    lines.append(
        f"- **Breaking changes:** {summary.breaking_count} "
        f"| **Severity:** {summary.highest_severity.value}"
    )
    if summary.bullet_points:
        lines.append("")
        lines.append("**Highlights:**")
        for bp in summary.bullet_points:
            lines.append(f"- {bp}")
    return "\n".join(lines)
