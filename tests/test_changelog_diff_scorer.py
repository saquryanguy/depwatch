"""Tests for depwatch.changelog_diff_scorer."""
from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from depwatch.changelog_diff import ChangelogDiff
from depwatch.changelog_diff_scorer import (
    DiffScoreEntry,
    DiffScoreReport,
    build_diff_score_report,
    format_diff_score_report,
)
from depwatch.severity_classifier import Severity


def _make_diff(
    package: str = "mypkg",
    old: str = "1.0.0",
    new: str = "2.0.0",
    lines: list[str] | None = None,
) -> ChangelogDiff:
    d = MagicMock(spec=ChangelogDiff)
    d.package = package
    d.old_version = old
    d.new_version = new
    d.lines = lines if lines is not None else []
    return d


# --- DiffScoreEntry ---

def test_diff_score_entry_package_delegates_to_diff():
    diff = _make_diff(package="requests")
    from depwatch.changelog_scorer import ChangelogScore
    score = ChangelogScore(package="requests", risk_score=0, risk_label="safe", breaking_count=0, total_lines=0)
    entry = DiffScoreEntry(diff=diff, score=score)
    assert entry.package == "requests"


def test_diff_score_entry_is_risky_false_when_score_zero():
    diff = _make_diff()
    from depwatch.changelog_scorer import ChangelogScore
    score = ChangelogScore(package="mypkg", risk_score=0, risk_label="safe", breaking_count=0, total_lines=0)
    entry = DiffScoreEntry(diff=diff, score=score)
    assert entry.is_risky is False


def test_diff_score_entry_is_risky_true_when_score_positive():
    diff = _make_diff()
    from depwatch.changelog_scorer import ChangelogScore
    score = ChangelogScore(package="mypkg", risk_score=5, risk_label="medium", breaking_count=1, total_lines=3)
    entry = DiffScoreEntry(diff=diff, score=score)
    assert entry.is_risky is True


# --- build_diff_score_report ---

def test_build_diff_score_report_empty_diffs():
    report = build_diff_score_report([])
    assert isinstance(report, DiffScoreReport)
    assert report.total == 0
    assert report.risky_count == 0
    assert report.overall_severity == Severity.SAFE


def test_build_diff_score_report_counts_entries():
    diffs = [_make_diff("pkgA"), _make_diff("pkgB")]
    report = build_diff_score_report(diffs)
    assert report.total == 2


def test_build_diff_score_report_entries_sorted_by_risk_descending():
    safe_diff = _make_diff("safe-pkg", lines=[])
    risky_diff = _make_diff("risky-pkg", lines=["Removed deprecated API foo", "Breaking change in bar"])
    report = build_diff_score_report([safe_diff, risky_diff])
    assert report.entries[0].package == "risky-pkg"


def test_build_diff_score_report_overall_severity_critical_for_breaking():
    diff = _make_diff(lines=["Removed deprecated API", "Breaking change in core"])
    report = build_diff_score_report([diff])
    assert report.overall_severity in (Severity.CRITICAL, Severity.HIGH)


def test_build_diff_score_report_risky_count():
    safe = _make_diff("safe", lines=[])
    risky = _make_diff("risky", lines=["Breaking change"])
    report = build_diff_score_report([safe, risky])
    assert report.risky_count >= 1


# --- format_diff_score_report ---

def test_format_diff_score_report_empty_returns_no_upgrades_message():
    report = DiffScoreReport(entries=[], overall_severity=Severity.SAFE)
    text = format_diff_score_report(report)
    assert "No dependency upgrades" in text


def test_format_diff_score_report_contains_package_name():
    diff = _make_diff("boto3", "1.0", "2.0")
    report = build_diff_score_report([diff])
    text = format_diff_score_report(report)
    assert "boto3" in text


def test_format_diff_score_report_contains_table_header():
    diff = _make_diff()
    report = build_diff_score_report([diff])
    text = format_diff_score_report(report)
    assert "Package" in text and "Risk" in text


def test_format_diff_score_report_contains_overall_severity():
    report = build_diff_score_report([])
    report.overall_severity = Severity.SAFE
    # rebuild manually to test non-empty
    diff = _make_diff("x")
    report2 = build_diff_score_report([diff])
    text = format_diff_score_report(report2)
    assert "Overall severity" in text
