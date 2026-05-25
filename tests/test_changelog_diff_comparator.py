"""Tests for changelog_diff_comparator."""
import pytest
from depwatch.changelog_diff import ChangelogDiff
from depwatch.changelog_diff_comparator import (
    compare_diffs,
    ComparisonEntry,
    ComparisonReport,
)
from depwatch.severity_classifier import Severity


def _make_diff(package: str, lines: list, old: str = "1.0", new: str = "2.0") -> ChangelogDiff:
    return ChangelogDiff(package=package, old_version=old, new_version=new, lines=lines)


def test_compare_diffs_empty_returns_empty_report():
    report = compare_diffs([], [])
    assert isinstance(report, ComparisonReport)
    assert report.entries == []


def test_compare_diffs_detects_new_package():
    new = [_make_diff("requests", [])]
    report = compare_diffs([], new)
    assert "requests" in report.packages_added


def test_compare_diffs_detects_removed_package():
    old = [_make_diff("requests", [])]
    report = compare_diffs(old, [])
    assert "requests" in report.packages_removed


def test_compare_diffs_common_package_creates_entry():
    old = [_make_diff("requests", [])]
    new = [_make_diff("requests", ["Removed old API"])]
    report = compare_diffs(old, new)
    assert len(report.entries) == 1
    assert report.entries[0].package == "requests"


def test_compare_diffs_regression_detected():
    old = [_make_diff("requests", [])]
    new = [_make_diff("requests", ["Breaking change: removed method"])]
    report = compare_diffs(old, new)
    assert report.entries[0].regressed


def test_compare_diffs_improvement_detected():
    old = [_make_diff("requests", ["Breaking change: removed method"])]
    new = [_make_diff("requests", [])]
    report = compare_diffs(old, new)
    assert report.entries[0].improved


def test_compare_diffs_added_lines():
    old = [_make_diff("pkg", ["line A"])]
    new = [_make_diff("pkg", ["line A", "line B"])]
    report = compare_diffs(old, new)
    assert "line B" in report.entries[0].added_lines


def test_compare_diffs_removed_lines():
    old = [_make_diff("pkg", ["line A", "line B"])]
    new = [_make_diff("pkg", ["line A"])]
    report = compare_diffs(old, new)
    assert "line B" in report.entries[0].removed_lines


def test_regressions_property():
    old = [_make_diff("pkg", [])]
    new = [_make_diff("pkg", ["Removed old API"])]
    report = compare_diffs(old, new)
    assert len(report.regressions) == 1


def test_improvements_property():
    old = [_make_diff("pkg", ["Removed old API"])]
    new = [_make_diff("pkg", [])]
    report = compare_diffs(old, new)
    assert len(report.improvements) == 1
