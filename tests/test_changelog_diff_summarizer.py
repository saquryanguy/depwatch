"""Tests for depwatch.changelog_diff_summarizer."""
from __future__ import annotations

import pytest

from depwatch.changelog_diff import ChangelogDiff
from depwatch.severity_classifier import Severity
from depwatch.changelog_diff_summarizer import (
    DiffSummaryEntry,
    DiffSummaryReport,
    summarize_diff,
    build_diff_summary_report,
    format_diff_summary_report,
)


def _make_diff(package="requests", old="1.0", new="2.0", lines=None):
    return ChangelogDiff(
        package=package,
        old_version=old,
        new_version=new,
        lines=lines or [],
    )


def test_summarize_diff_returns_entry():
    diff = _make_diff()
    entry = summarize_diff(diff)
    assert isinstance(entry, DiffSummaryEntry)


def test_summarize_diff_sets_package_and_versions():
    diff = _make_diff(package="flask", old="1.0", new="2.0")
    entry = summarize_diff(diff)
    assert entry.package == "flask"
    assert entry.old_version == "1.0"
    assert entry.new_version == "2.0"


def test_summarize_diff_empty_lines_is_safe():
    diff = _make_diff(lines=[])
    entry = summarize_diff(diff)
    assert entry.is_safe
    assert entry.breaking_count == 0
    assert entry.highest_severity == Severity.SAFE


def test_summarize_diff_detects_breaking():
    diff = _make_diff(lines=["- Removed support for Python 2", "Breaking change in API"])
    entry = summarize_diff(diff)
    assert not entry.is_safe
    assert entry.breaking_count > 0


def test_summarize_diff_headline_extracted():
    diff = _make_diff(lines=["### Breaking changes", "Removed the old API endpoint"])
    entry = summarize_diff(diff)
    assert entry.headline is not None
    assert len(entry.headline) > 0


def test_summarize_diff_no_headline_for_empty():
    diff = _make_diff(lines=[])
    entry = summarize_diff(diff)
    assert entry.headline is None


def test_build_diff_summary_report_empty():
    report = build_diff_summary_report([])
    assert isinstance(report, DiffSummaryReport)
    assert report.total_packages == 0
    assert report.affected_packages == 0
    assert report.overall_severity == Severity.SAFE


def test_build_diff_summary_report_counts_packages():
    diffs = [_make_diff("a"), _make_diff("b"), _make_diff("c")]
    report = build_diff_summary_report(diffs)
    assert report.total_packages == 3


def test_build_diff_summary_report_counts_affected():
    safe_diff = _make_diff("safe", lines=[])
    breaking_diff = _make_diff("breaking", lines=["Removed deprecated method"])
    report = build_diff_summary_report([safe_diff, breaking_diff])
    assert report.affected_packages == 1


def test_build_diff_summary_report_overall_severity():
    diffs = [_make_diff(lines=["Breaking change: removed API"])]
    report = build_diff_summary_report(diffs)
    assert report.overall_severity != Severity.SAFE


def test_format_diff_summary_report_empty():
    report = build_diff_summary_report([])
    text = format_diff_summary_report(report)
    assert "No dependency changes" in text


def test_format_diff_summary_report_contains_package():
    diffs = [_make_diff("mypackage", "1.0", "2.0")]
    report = build_diff_summary_report(diffs)
    text = format_diff_summary_report(report)
    assert "mypackage" in text


def test_format_diff_summary_report_contains_versions():
    diffs = [_make_diff("pkg", "1.2.3", "4.5.6")]
    report = build_diff_summary_report(diffs)
    text = format_diff_summary_report(report)
    assert "1.2.3" in text
    assert "4.5.6" in text


def test_format_diff_summary_report_contains_severity():
    diffs = [_make_diff(lines=[])]
    report = build_diff_summary_report(diffs)
    text = format_diff_summary_report(report)
    assert "SAFE" in text
