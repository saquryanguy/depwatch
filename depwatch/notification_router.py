"""Routes severity reports to appropriate notification channels based on severity thresholds."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from depwatch.severity_classifier import Severity
from depwatch.severity_report import SeverityReport


@dataclass
class NotificationTarget:
    """Represents a notification destination with a severity threshold."""

    channel: str  # e.g. "pr_comment", "stdout", "slack"
    min_severity: Severity = Severity.LOW
    label: Optional[str] = None

    def should_notify(self, severity: Severity) -> bool:
        """Return True if the given severity meets or exceeds this target's threshold."""
        _rank = {
            Severity.LOW: 0,
            Severity.MEDIUM: 1,
            Severity.HIGH: 2,
            Severity.CRITICAL: 3,
        }
        return _rank[severity] >= _rank[self.min_severity]


@dataclass
class RoutingResult:
    """Holds the routing decision for a single report."""

    report: SeverityReport
    targets: List[NotificationTarget] = field(default_factory=list)

    @property
    def has_targets(self) -> bool:
        return len(self.targets) > 0


def route_report(
    report: SeverityReport,
    targets: List[NotificationTarget],
) -> RoutingResult:
    """Determine which targets should receive a notification for the given report."""
    matched = [
        t for t in targets if t.should_notify(report.highest_severity)
    ]
    return RoutingResult(report=report, targets=matched)


def route_reports(
    reports: List[SeverityReport],
    targets: List[NotificationTarget],
) -> List[RoutingResult]:
    """Route a list of severity reports, returning only results with at least one target."""
    results = [route_report(r, targets) for r in reports]
    return [res for res in results if res.has_targets]


def default_targets_from_env() -> List[NotificationTarget]:
    """Build a default target list: always notify stdout; PR comment for HIGH+."""
    return [
        NotificationTarget(channel="stdout", min_severity=Severity.LOW, label="console"),
        NotificationTarget(channel="pr_comment", min_severity=Severity.HIGH, label="pr"),
    ]
