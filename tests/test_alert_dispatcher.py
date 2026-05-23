"""Tests for depwatch.alert_dispatcher."""

from __future__ import annotations

import pytest

from depwatch.alert_dispatcher import (
    DispatchResult,
    dispatch_alert,
    dispatch_alerts,
)
from depwatch.notification_router import NotificationTarget, RoutingResult
from depwatch.severity_classifier import Severity
from depwatch.severity_report import SeverityReport


def _make_report(package: str = "requests", severity: Severity = Severity.HIGH) -> SeverityReport:
    return SeverityReport(
        package=package,
        old_version="1.0.0",
        new_version="2.0.0",
        highest_severity=severity,
        annotated_lines=[],
    )


def _make_routing(*targets: NotificationTarget) -> RoutingResult:
    return RoutingResult(targets=list(targets))


# ---------------------------------------------------------------------------
# DispatchResult
# ---------------------------------------------------------------------------

def test_dispatch_result_success_when_no_errors():
    r = DispatchResult(package="pkg", targets_notified=["slack"])
    assert r.success is True


def test_dispatch_result_failure_when_errors():
    r = DispatchResult(package="pkg", errors=["slack: timeout"])
    assert r.success is False


def test_dispatch_result_any_notified_true():
    r = DispatchResult(package="pkg", targets_notified=["slack"])
    assert r.any_notified is True


def test_dispatch_result_any_notified_false():
    r = DispatchResult(package="pkg")
    assert r.any_notified is False


# ---------------------------------------------------------------------------
# dispatch_alert
# ---------------------------------------------------------------------------

def test_dispatch_alert_no_targets_returns_empty():
    report = _make_report()
    routing = _make_routing()
    result = dispatch_alert(report, routing)
    assert result.targets_notified == []
    assert result.targets_skipped == []
    assert result.errors == []


def test_dispatch_alert_dry_run_notifies_without_side_effects():
    report = _make_report()
    routing = _make_routing(NotificationTarget.STDOUT)
    result = dispatch_alert(report, routing, dry_run=True)
    assert result.any_notified is True
    assert NotificationTarget.STDOUT.value in result.targets_notified
    assert result.errors == []


def test_dispatch_alert_records_package_name():
    report = _make_report(package="boto3")
    routing = _make_routing()
    result = dispatch_alert(report, routing)
    assert result.package == "boto3"


def test_dispatch_alert_multiple_targets_all_notified():
    report = _make_report()
    routing = _make_routing(NotificationTarget.STDOUT, NotificationTarget.STDOUT)
    result = dispatch_alert(report, routing, dry_run=True)
    assert len(result.targets_notified) == 2


# ---------------------------------------------------------------------------
# dispatch_alerts
# ---------------------------------------------------------------------------

def test_dispatch_alerts_returns_one_result_per_report():
    reports = [_make_report("pkg-a"), _make_report("pkg-b")]
    routings = [_make_routing(NotificationTarget.STDOUT), _make_routing()]
    results = dispatch_alerts(reports, routings, dry_run=True)
    assert len(results) == 2


def test_dispatch_alerts_raises_on_length_mismatch():
    reports = [_make_report()]
    routings = []
    with pytest.raises(ValueError, match="equal length"):
        dispatch_alerts(reports, routings)


def test_dispatch_alerts_preserves_order():
    reports = [_make_report("a"), _make_report("b")]
    routings = [_make_routing(), _make_routing()]
    results = dispatch_alerts(reports, routings)
    assert results[0].package == "a"
    assert results[1].package == "b"
