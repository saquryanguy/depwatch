"""Tests for depwatch.changelog_diff_filter."""

import pytest
from unittest.mock import MagicMock

from depwatch.changelog_diff import ChangelogDiff
from depwatch.changelog_diff_scorer import DiffScoreEntry
from depwatch.changelog_diff_filter import (
    DiffFilterCriteria,
    FilteredDiffReport,
    filter_diff_entries,
    filter_changelog_diffs,
)


def _make_entry(package: str, score: float) -> DiffScoreEntry:
    diff = MagicMock(spec=ChangelogDiff)
    diff.package = package
    entry = MagicMock(spec=DiffScoreEntry)
    entry.package = package
    entry.score = score
    entry.is_risky = score > 0
    return entry


def _make_diff(package: str, lines: list) -> ChangelogDiff:
    diff = MagicMock(spec=ChangelogDiff)
    diff.package = package
    diff.lines = lines
    diff.found = bool(lines)
    return diff


# --- FilteredDiffReport properties ---

def test_filtered_diff_report_total_input():
    criteria = DiffFilterCriteria()
    report = FilteredDiffReport(criteria=criteria)
    report.included = [_make_entry("a", 1.0), _make_entry("b", 2.0)]
    report.excluded = [_make_entry("c", 0.0)]
    assert report.total_input == 3


def test_filtered_diff_report_has_risky_true():
    criteria = DiffFilterCriteria()
    report = FilteredDiffReport(criteria=criteria)
    report.included = [_make_entry("a", 5.0)]
    assert report.has_risky is True


def test_filtered_diff_report_has_risky_false():
    criteria = DiffFilterCriteria()
    report = FilteredDiffReport(criteria=criteria)
    report.included = [_make_entry("a", 0.0)]
    assert report.has_risky is False


# --- filter_diff_entries ---

def test_filter_diff_entries_no_criteria_includes_all():
    entries = [_make_entry("pkg-a", 0.0), _make_entry("pkg-b", 3.0)]
    criteria = DiffFilterCriteria()
    result = filter_diff_entries(entries, criteria)
    assert len(result.included) == 2
    assert len(result.excluded) == 0


def test_filter_diff_entries_min_score_excludes_low():
    entries = [_make_entry("a", 1.0), _make_entry("b", 5.0)]
    criteria = DiffFilterCriteria(min_score=3.0)
    result = filter_diff_entries(entries, criteria)
    assert len(result.included) == 1
    assert result.included[0].package == "b"


def test_filter_diff_entries_only_risky_excludes_safe():
    entries = [_make_entry("safe", 0.0), _make_entry("risky", 2.0)]
    criteria = DiffFilterCriteria(only_risky=True)
    result = filter_diff_entries(entries, criteria)
    assert len(result.included) == 1
    assert result.included[0].package == "risky"


def test_filter_diff_entries_excluded_packages_removed():
    entries = [_make_entry("requests", 4.0), _make_entry("flask", 4.0)]
    criteria = DiffFilterCriteria(excluded_packages=["requests"])
    result = filter_diff_entries(entries, criteria)
    assert len(result.included) == 1
    assert result.included[0].package == "flask"


def test_filter_diff_entries_excluded_packages_normalizes_name():
    entries = [_make_entry("my-package", 4.0)]
    criteria = DiffFilterCriteria(excluded_packages=["my_package"])
    result = filter_diff_entries(entries, criteria)
    assert len(result.included) == 0


def test_filter_diff_entries_max_results_limits_included():
    entries = [_make_entry(f"pkg{i}", float(i)) for i in range(5)]
    criteria = DiffFilterCriteria(max_results=3)
    result = filter_diff_entries(entries, criteria)
    assert len(result.included) == 3
    assert len(result.excluded) == 2


def test_filter_diff_entries_empty_input_returns_empty():
    criteria = DiffFilterCriteria(min_score=1.0, only_risky=True)
    result = filter_diff_entries([], criteria)
    assert result.included == []
    assert result.excluded == []
    assert result.total_input == 0


# --- filter_changelog_diffs integration ---

def test_filter_changelog_diffs_returns_filtered_report():
    diffs = [
        _make_diff("requests", ["- removed old_func"]),
        _make_diff("flask", []),
    ]
    criteria = DiffFilterCriteria()
    result = filter_changelog_diffs(diffs, criteria)
    assert isinstance(result, FilteredDiffReport)
    assert result.total_input == 2
