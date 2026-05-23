"""Dispatches alerts for dependency reports based on routing results."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import List, Optional

from depwatch.notification_router import RoutingResult, NotificationTarget
from depwatch.severity_report import SeverityReport

logger = logging.getLogger(__name__)


@dataclass
class DispatchResult:
    package: str
    targets_notified: List[str] = field(default_factory=list)
    targets_skipped: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

    @property
    def success(self) -> bool:
        return len(self.errors) == 0

    @property
    def any_notified(self) -> bool:
        return len(self.targets_notified) > 0


def _label_for_target(target: NotificationTarget) -> str:
    return target.value


def dispatch_alert(
    report: SeverityReport,
    routing: RoutingResult,
    dry_run: bool = False,
) -> DispatchResult:
    """Dispatch alert notifications for a single package report."""
    result = DispatchResult(package=report.package)

    if not routing.targets:
        logger.debug("No targets for package %s — skipping dispatch.", report.package)
        return result

    for target in routing.targets:
        label = _label_for_target(target)
        if dry_run:
            logger.info("[dry-run] Would notify %s for %s", label, report.package)
            result.targets_notified.append(label)
            continue
        try:
            logger.info("Dispatching alert to %s for %s", label, report.package)
            # Real integrations (Slack, email, etc.) would be called here.
            result.targets_notified.append(label)
        except Exception as exc:  # pragma: no cover
            msg = f"{label}: {exc}"
            logger.error("Dispatch error for %s — %s", report.package, msg)
            result.errors.append(msg)
            result.targets_skipped.append(label)

    return result


def dispatch_alerts(
    reports: List[SeverityReport],
    routings: List[RoutingResult],
    dry_run: bool = False,
) -> List[DispatchResult]:
    """Dispatch alerts for a list of reports paired with routing results."""
    if len(reports) != len(routings):
        raise ValueError("reports and routings must have equal length")
    return [
        dispatch_alert(report, routing, dry_run=dry_run)
        for report, routing in zip(reports, routings)
    ]
