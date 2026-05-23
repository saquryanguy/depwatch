"""Builds a severity-annotated report for a package's breaking changes."""

from dataclasses import dataclass, field
from typing import Dict, List, Tuple

from depwatch.severity_classifier import Severity, classify_changes, highest_severity


_SEVERITY_EMOJI: Dict[Severity, str] = {
    Severity.CRITICAL: "🔴",
    Severity.HIGH: "🟠",
    Severity.MEDIUM: "🟡",
    Severity.LOW: "🔵",
    Severity.SAFE: "🟢",
}


@dataclass
class SeverityReport:
    package: str
    old_version: str
    new_version: str
    annotated_lines: List[Tuple[str, Severity]] = field(default_factory=list)
    overall: Severity = Severity.SAFE


def build_severity_report(
    package: str,
    old_version: str,
    new_version: str,
    breaking_lines: List[str],
) -> SeverityReport:
    """Create a SeverityReport from a list of breaking change lines."""
    annotated = classify_changes(breaking_lines)
    overall = highest_severity(breaking_lines)
    return SeverityReport(
        package=package,
        old_version=old_version,
        new_version=new_version,
        annotated_lines=annotated,
        overall=overall,
    )


def format_severity_section(report: SeverityReport) -> str:
    """Render a SeverityReport as a Markdown section."""
    emoji = _SEVERITY_EMOJI[report.overall]
    lines = [
        f"### {emoji} `{report.package}` {report.old_version} → {report.new_version}",
        f"**Overall severity:** {report.overall.value.upper()}",
        "",
    ]
    if not report.annotated_lines:
        lines.append("_No breaking changes detected._")
    else:
        lines.append("| Severity | Change |")
        lines.append("|----------|--------|")
        for text, severity in report.annotated_lines:
            row_emoji = _SEVERITY_EMOJI[severity]
            escaped = text.replace("|", "\\|")
            lines.append(f"| {row_emoji} {severity.value} | {escaped} |")
    return "\n".join(lines)
