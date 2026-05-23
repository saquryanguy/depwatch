"""Tests for depwatch.run_summary."""

import pytest

from depwatch.severity_classifier import Severity
from depwatch.severity_report import SeverityReport
from depwatch.run_summary import RunSummary, build_run_summary, format_run_summary


def _make_report(package: str, lines, old="1.0", new="2.0") -> SeverityReport:
    from depwatch.severity_report import build_severity_report

    return build_severity_report(package, old, new, lines)


# ---------------------------------------------------------------------------
# build_run_summary
# ---------------------------------------------------------------------------

def test_build_run_summary_returns_run_summary():
    summary = build_run_summary([])
    assert isinstance(summary, RunSummary)


def test_build_run_summary_empty_reports():
    summary = build_run_summary([])
    assert summary.total_packages == 0
    assert summary.affected_packages == 0


def test_build_run_summary_counts_packages():
    reports = [
        _make_report("pkgA", []),
        _make_report("pkgB", []),
    ]
    summary = build_run_summary(reports)
    assert summary.total_packages == 2


def test_build_run_summary_counts_affected():
    reports = [
        _make_report("pkgA", ["Removed old_function"]),
        _make_report("pkgB", []),
    ]
    summary = build_run_summary(reports)
    assert summary.affected_packages == 1


def test_build_run_summary_highest_severity_critical():
    reports = [_make_report("pkgA", ["Breaking change: removed API"])]
    summary = build_run_summary(reports)
    assert summary.highest_severity == Severity.CRITICAL


def test_build_run_summary_highest_severity_safe_when_empty():
    summary = build_run_summary([])
    assert summary.highest_severity == Severity.SAFE


def test_build_run_summary_errors_stored():
    summary = build_run_summary([], errors=["timeout on pkgA"])
    assert summary.has_errors
    assert "timeout on pkgA" in summary.errors


def test_build_run_summary_no_errors_by_default():
    summary = build_run_summary([])
    assert not summary.has_errors


def test_is_clean_true_when_no_changes_no_errors():
    summary = build_run_summary([])
    assert summary.is_clean


def test_is_clean_false_when_affected():
    reports = [_make_report("pkgA", ["Removed foo"])]
    summary = build_run_summary(reports)
    assert not summary.is_clean


def test_is_clean_false_when_errors():
    summary = build_run_summary([], errors=["something went wrong"])
    assert not summary.is_clean


# ---------------------------------------------------------------------------
# format_run_summary
# ---------------------------------------------------------------------------

def test_format_run_summary_contains_header():
    summary = build_run_summary([])
    text = format_run_summary(summary)
    assert "depwatch run summary" in text


def test_format_run_summary_shows_status_clean():
    summary = build_run_summary([])
    text = format_run_summary(summary)
    assert "CLEAN" in text


def test_format_run_summary_shows_action_required():
    reports = [_make_report("pkgA", ["Removed foo"])]
    summary = build_run_summary(reports)
    text = format_run_summary(summary)
    assert "ACTION REQUIRED" in text


def test_format_run_summary_lists_errors():
    summary = build_run_summary([], errors=["network error"])
    text = format_run_summary(summary)
    assert "network error" in text


def test_format_run_summary_no_errors_line():
    summary = build_run_summary([])
    text = format_run_summary(summary)
    assert "none" in text
