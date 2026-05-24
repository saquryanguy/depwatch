"""Builds a structured annotation report from changelog lines for a package upgrade."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from depwatch.changelog_annotator import AnnotatedLine, annotate_lines, filter_annotated
from depwatch.severity_classifier import Severity, highest_severity


@dataclass
class AnnotationReport:
    package: str
    old_version: str
    new_version: str
    annotated_lines: List[AnnotatedLine] = field(default_factory=list)
    highest_severity: Severity = Severity.LOW
    category_counts: Dict[str, int] = field(default_factory=dict)


def _count_categories(annotated: List[AnnotatedLine]) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for al in annotated:
        for cat in al.categories:
            counts[cat] = counts.get(cat, 0) + 1
    return counts


def build_annotation_report(
    package: str,
    old_version: str,
    new_version: str,
    lines: List[str],
    min_severity: Severity = Severity.LOW,
    categories: Optional[List[str]] = None,
) -> AnnotationReport:
    """Annotate changelog lines and build a structured report."""
    all_annotated = annotate_lines(lines)
    filtered = filter_annotated(all_annotated, min_severity=min_severity, categories=categories)

    top_severity = highest_severity([al.severity for al in filtered]) if filtered else Severity.LOW
    cat_counts = _count_categories(filtered)

    return AnnotationReport(
        package=package,
        old_version=old_version,
        new_version=new_version,
        annotated_lines=filtered,
        highest_severity=top_severity,
        category_counts=cat_counts,
    )


def format_annotation_report(report: AnnotationReport) -> str:
    """Format an AnnotationReport as a markdown string."""
    lines = [
        f"### {report.package} ({report.old_version} → {report.new_version})",
        f"**Highest severity:** {report.highest_severity.value}",
    ]

    if report.category_counts:
        cats = ", ".join(
            f"{cat}: {count}" for cat, count in sorted(report.category_counts.items())
        )
        lines.append(f"**Categories:** {cats}")

    if report.annotated_lines:
        lines.append("")
        lines.append("| # | Severity | Categories | Change |")
        lines.append("|---|----------|------------|--------|")
        for al in report.annotated_lines:
            cats_str = ", ".join(al.categories) if al.categories else "—"
            text = al.text.replace("|", "\\|")
            lines.append(f"| {al.line_number} | {al.severity.value} | {cats_str} | {text} |")
    else:
        lines.append("\n_No notable changes found._")

    return "\n".join(lines)
