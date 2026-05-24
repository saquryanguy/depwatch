"""Tests for depwatch.changelog_diff_merger."""
from __future__ import annotations

from depwatch.changelog_diff import ChangelogDiff
from depwatch.changelog_diff_merger import (
    MergedDiff,
    MergedDiffReport,
    merge_diffs,
)
from depwatch.severity_classifier import Severity


def _make_diff(
    package: str = "requests",
    from_version: str = "2.0.0",
    to_version: str = "2.1.0",
    lines: list[str] | None = None,
) -> ChangelogDiff:
    return ChangelogDiff(
        package=package,
        from_version=from_version,
        to_version=to_version,
        lines=lines or [],
    )


def test_merge_diffs_empty_returns_empty_report():
    report = merge_diffs([])
    assert isinstance(report, MergedDiffReport)
    assert report.total == 0
    assert report.packages == []


def test_merge_diffs_single_diff_creates_entry():
    diff = _make_diff(lines=["- Added feature"])
    report = merge_diffs([diff])
    assert "requests" in report.entries
    assert isinstance(report.entries["requests"], MergedDiff)


def test_merge_diffs_preserves_versions():
    diff = _make_diff(from_version="1.0.0", to_version="2.0.0")
    report = merge_diffs([diff])
    entry = report.entries["requests"]
    assert entry.from_version == "1.0.0"
    assert entry.to_version == "2.0.0"


def test_merge_diffs_combines_lines_for_same_package():
    d1 = _make_diff(from_version="1.0", to_version="1.1", lines=["line A"])
    d2 = _make_diff(from_version="1.1", to_version="1.2", lines=["line B"])
    report = merge_diffs([d1, d2])
    entry = report.entries["requests"]
    assert "line A" in entry.lines
    assert "line B" in entry.lines


def test_merge_diffs_different_packages_creates_separate_entries():
    d1 = _make_diff(package="requests")
    d2 = _make_diff(package="flask")
    report = merge_diffs([d1, d2])
    assert "requests" in report.entries
    assert "flask" in report.entries
    assert report.total == 2


def test_merge_diffs_has_breaking_false_when_all_safe():
    diff = _make_diff(lines=["Added new helper method"])
    report = merge_diffs([diff])
    assert report.has_breaking is False


def test_merge_diffs_has_breaking_true_when_breaking_line():
    diff = _make_diff(lines=["Removed deprecated API endpoint"])
    report = merge_diffs([diff])
    assert report.has_breaking is True


def test_merge_diffs_severity_critical_for_breaking():
    diff = _make_diff(lines=["Breaking change: removed `get_user` function"])
    report = merge_diffs([diff])
    entry = report.entries["requests"]
    assert entry.severity == Severity.CRITICAL


def test_merge_diffs_is_empty_true_when_no_lines():
    diff = _make_diff(lines=[])
    report = merge_diffs([diff])
    assert report.entries["requests"].is_empty is True


def test_merge_diffs_is_empty_false_when_lines_present():
    diff = _make_diff(lines=["something changed"])
    report = merge_diffs([diff])
    assert report.entries["requests"].is_empty is False


def test_merge_diffs_packages_property_lists_all():
    diffs = [
        _make_diff(package="a"),
        _make_diff(package="b"),
        _make_diff(package="c"),
    ]
    report = merge_diffs(diffs)
    assert sorted(report.packages) == ["a", "b", "c"]
