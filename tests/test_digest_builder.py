"""Tests for depwatch.digest_builder."""

import pytest

from depwatch.severity_classifier import Severity
from depwatch.severity_report import SeverityReport
from depwatch.digest_builder import (
    DigestSummary,
    build_digest,
    format_digest_markdown,
)


def _make_report(package: str, severity: Severity) -> SeverityReport:
    return SeverityReport(
        package=package,
        from_version="1.0.0",
        to_version="2.0.0",
        annotated_lines=[],
        highest_severity=severity,
    )


def test_build_digest_empty_returns_default():
    digest = build_digest([])
    assert digest.total_packages == 0
    assert digest.affected_packages == 0
    assert digest.overall_severity == Severity.SAFE


def test_build_digest_counts_packages():
    reports = [
        _make_report("requests", Severity.SAFE),
        _make_report("flask", Severity.HIGH),
    ]
    digest = build_digest(reports)
    assert digest.total_packages == 2


def test_build_digest_counts_affected():
    reports = [
        _make_report("requests", Severity.SAFE),
        _make_report("flask", Severity.HIGH),
        _make_report("django", Severity.CRITICAL),
    ]
    digest = build_digest(reports)
    assert digest.affected_packages == 2


def test_build_digest_overall_severity_is_highest():
    reports = [
        _make_report("a", Severity.LOW),
        _make_report("b", Severity.CRITICAL),
        _make_report("c", Severity.MEDIUM),
    ]
    digest = build_digest(reports)
    assert digest.overall_severity == Severity.CRITICAL


def test_build_digest_critical_packages_list():
    reports = [
        _make_report("alpha", Severity.CRITICAL),
        _make_report("beta", Severity.HIGH),
    ]
    digest = build_digest(reports)
    assert "alpha" in digest.critical_packages
    assert "beta" not in digest.critical_packages


def test_build_digest_high_packages_list():
    reports = [
        _make_report("alpha", Severity.CRITICAL),
        _make_report("beta", Severity.HIGH),
    ]
    digest = build_digest(reports)
    assert "beta" in digest.high_packages
    assert "alpha" not in digest.high_packages


def test_format_digest_markdown_contains_header():
    digest = build_digest([])
    md = format_digest_markdown(digest)
    assert "## DepWatch Digest" in md


def test_format_digest_markdown_shows_safe_message_when_no_issues():
    reports = [_make_report("requests", Severity.SAFE)]
    digest = build_digest(reports)
    md = format_digest_markdown(digest)
    assert "No critical or high severity" in md


def test_format_digest_markdown_shows_critical_package():
    reports = [_make_report("django", Severity.CRITICAL)]
    digest = build_digest(reports)
    md = format_digest_markdown(digest)
    assert "django" in md
    assert "Critical" in md


def test_format_digest_markdown_contains_footer():
    digest = build_digest([])
    md = format_digest_markdown(digest)
    assert "depwatch" in md.lower()
