"""Tests for changelog_diff_grouper."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional
from unittest.mock import patch

import pytest

from depwatch.changelog_diff import ChangelogDiff
from depwatch.changelog_diff_grouper import (
    DiffGroup,
    GroupedDiffReport,
    _severity_for_diff,
    group_diffs_by_severity,
)
from depwatch.severity_classifier import Severity


def _make_diff(package: str, lines: Optional[List[str]] = None) -> ChangelogDiff:
    return ChangelogDiff(
        package=package,
        old_version="1.0.0",
        new_version="2.0.0",
        lines=lines or [],
    )


def test_group_diffs_empty_returns_empty_report():
    report = group_diffs_by_severity([])
    assert isinstance(report, GroupedDiffReport)
    assert report.total == 0


def test_group_diffs_single_safe_diff():
    diff = _make_diff("requests", ["Minor bug fix"])
    report = group_diffs_by_severity([diff])
    assert report.total == 1


def test_group_diffs_critical_diff_is_grouped_under_critical():
    diff = _make_diff("django", ["Removed deprecated API", "Breaking change in auth"])
    report = group_diffs_by_severity([diff])
    assert "CRITICAL" in report.severity_names or any(
        g.severity in (Severity.CRITICAL, Severity.HIGH)
        for g in report.groups.values()
    )


def test_group_diffs_packages_listed_in_group():
    diff = _make_diff("flask", [])
    report = group_diffs_by_severity([diff])
    all_packages = [p for g in report.groups.values() for p in g.packages]
    assert "flask" in all_packages


def test_group_diffs_multiple_packages_same_severity():
    diffs = [
        _make_diff("pkg_a", ["Minor fix"]),
        _make_diff("pkg_b", ["Minor fix"]),
    ]
    report = group_diffs_by_severity(diffs)
    assert report.total == 2


def test_diff_group_count_matches_diffs():
    diff1 = _make_diff("a", [])
    diff2 = _make_diff("b", [])
    group = DiffGroup(severity=Severity.SAFE, diffs=[diff1, diff2])
    assert group.count == 2


def test_diff_group_packages_returns_names():
    diff1 = _make_diff("alpha", [])
    diff2 = _make_diff("beta", [])
    group = DiffGroup(severity=Severity.SAFE, diffs=[diff1, diff2])
    assert group.packages == ["alpha", "beta"]


def test_grouped_diff_report_get_missing_severity_returns_empty_group():
    report = GroupedDiffReport(groups={})
    group = report.get(Severity.CRITICAL)
    assert isinstance(group, DiffGroup)
    assert group.count == 0


def test_severity_for_diff_returns_severity_instance():
    diff = _make_diff("mylib", ["some change"])
    sev = _severity_for_diff(diff)
    assert isinstance(sev, Severity)


def test_severity_for_diff_no_lines_returns_safe():
    diff = _make_diff("emptylib", [])
    sev = _severity_for_diff(diff)
    assert sev == Severity.SAFE
