"""Tests for depwatch.notification_router."""

from __future__ import annotations

import pytest

from depwatch.severity_classifier import Severity
from depwatch.severity_report import SeverityReport
from depwatch.notification_router import (
    NotificationTarget,
    RoutingResult,
    route_report,
    route_reports,
    default_targets_from_env,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_report(package: str, severity: Severity) -> SeverityReport:
    return SeverityReport(
        package=package,
        old_version="1.0.0",
        new_version="2.0.0",
        highest_severity=severity,
        annotated_lines=[],
    )


# ---------------------------------------------------------------------------
# NotificationTarget.should_notify
# ---------------------------------------------------------------------------

def test_should_notify_exact_match():
    target = NotificationTarget(channel="stdout", min_severity=Severity.HIGH)
    assert target.should_notify(Severity.HIGH) is True


def test_should_notify_above_threshold():
    target = NotificationTarget(channel="pr_comment", min_severity=Severity.HIGH)
    assert target.should_notify(Severity.CRITICAL) is True


def test_should_notify_below_threshold():
    target = NotificationTarget(channel="pr_comment", min_severity=Severity.HIGH)
    assert target.should_notify(Severity.MEDIUM) is False


def test_should_notify_low_threshold_accepts_all():
    target = NotificationTarget(channel="stdout", min_severity=Severity.LOW)
    for sev in Severity:
        assert target.should_notify(sev) is True


# ---------------------------------------------------------------------------
# route_report
# ---------------------------------------------------------------------------

def test_route_report_matches_correct_targets():
    targets = [
        NotificationTarget(channel="stdout", min_severity=Severity.LOW),
        NotificationTarget(channel="pr_comment", min_severity=Severity.HIGH),
    ]
    report = _make_report("requests", Severity.HIGH)
    result = route_report(report, targets)
    assert len(result.targets) == 2


def test_route_report_low_severity_skips_high_target():
    targets = [
        NotificationTarget(channel="stdout", min_severity=Severity.LOW),
        NotificationTarget(channel="pr_comment", min_severity=Severity.HIGH),
    ]
    report = _make_report("requests", Severity.LOW)
    result = route_report(report, targets)
    channels = [t.channel for t in result.targets]
    assert "stdout" in channels
    assert "pr_comment" not in channels


def test_route_report_no_targets_when_all_thresholds_too_high():
    targets = [
        NotificationTarget(channel="pagerduty", min_severity=Severity.CRITICAL),
    ]
    report = _make_report("boto3", Severity.MEDIUM)
    result = route_report(report, targets)
    assert result.has_targets is False


def test_route_report_preserves_report_reference():
    report = _make_report("django", Severity.CRITICAL)
    result = route_report(report, [])
    assert result.report is report


# ---------------------------------------------------------------------------
# route_reports
# ---------------------------------------------------------------------------

def test_route_reports_filters_out_empty_results():
    targets = [NotificationTarget(channel="pr_comment", min_severity=Severity.CRITICAL)]
    reports = [
        _make_report("safe-pkg", Severity.LOW),
        _make_report("dangerous-pkg", Severity.CRITICAL),
    ]
    results = route_reports(reports, targets)
    assert len(results) == 1
    assert results[0].report.package == "dangerous-pkg"


def test_route_reports_empty_list_returns_empty():
    targets = [NotificationTarget(channel="stdout", min_severity=Severity.LOW)]
    assert route_reports([], targets) == []


# ---------------------------------------------------------------------------
# default_targets_from_env
# ---------------------------------------------------------------------------

def test_default_targets_from_env_returns_two_targets():
    targets = default_targets_from_env()
    assert len(targets) == 2


def test_default_targets_from_env_includes_stdout_and_pr_comment():
    targets = default_targets_from_env()
    channels = {t.channel for t in targets}
    assert "stdout" in channels
    assert "pr_comment" in channels


def test_default_targets_stdout_has_low_threshold():
    targets = default_targets_from_env()
    stdout_target = next(t for t in targets if t.channel == "stdout")
    assert stdout_target.min_severity == Severity.LOW
