"""Builds a final run summary after the full pipeline has executed."""

from dataclasses import dataclass, field
from typing import List, Optional

from depwatch.severity_classifier import Severity
from depwatch.severity_report import SeverityReport
from depwatch.digest_builder import DigestSummary, build_digest


@dataclass
class RunSummary:
    """Aggregated result of a single depwatch run."""

    total_packages: int
    affected_packages: int
    highest_severity: Severity
    digest: DigestSummary
    errors: List[str] = field(default_factory=list)

    @property
    def has_errors(self) -> bool:
        return bool(self.errors)

    @property
    def is_clean(self) -> bool:
        """True when no breaking changes were detected and no errors occurred."""
        return self.affected_packages == 0 and not self.has_errors


def build_run_summary(
    reports: List[SeverityReport],
    errors: Optional[List[str]] = None,
) -> RunSummary:
    """Build a RunSummary from a list of SeverityReports.

    Args:
        reports: All per-package severity reports produced by the pipeline.
        errors: Optional list of error messages collected during the run.

    Returns:
        A populated RunSummary instance.
    """
    digest = build_digest(reports)
    return RunSummary(
        total_packages=digest.total_packages,
        affected_packages=digest.affected_packages,
        highest_severity=digest.overall_severity,
        digest=digest,
        errors=list(errors or []),
    )


def format_run_summary(summary: RunSummary) -> str:
    """Return a human-readable plain-text representation of the run summary."""
    lines = [
        "=== depwatch run summary ===",
        f"Packages checked : {summary.total_packages}",
        f"Packages affected: {summary.affected_packages}",
        f"Highest severity : {summary.highest_severity.value}",
    ]
    if summary.errors:
        lines.append(f"Errors           : {len(summary.errors)}")
        for err in summary.errors:
            lines.append(f"  - {err}")
    else:
        lines.append("Errors           : none")
    status = "CLEAN" if summary.is_clean else "ACTION REQUIRED"
    lines.append(f"Status           : {status}")
    return "\n".join(lines)
