"""Tests for depwatch.changelog_scorer."""

import pytest
from depwatch.changelog_scorer import (
    ChangelogScore,
    _risk_label,
    score_changelog_diff,
    score_changelog_diffs,
    top_risk_packages,
)
from depwatch.changelog_diff import ChangelogDiff


def _make_diff(package="mypkg", old="1.0.0", new="2.0.0", lines=None):
    return ChangelogDiff(
        package=package,
        old_version=old,
        new_version=new,
        lines=lines or [],
        found=bool(lines),
    )


# --- _risk_label ---

def test_risk_label_safe():
    assert _risk_label(0) == "safe"


def test_risk_label_low():
    assert _risk_label(3) == "low"


def test_risk_label_medium():
    assert _risk_label(10) == "medium"


def test_risk_label_high():
    assert _risk_label(20) == "high"


def test_risk_label_critical():
    assert _risk_label(30) == "critical"


# --- score_changelog_diff ---

def test_score_changelog_diff_returns_dataclass():
    diff = _make_diff()
    result = score_changelog_diff(diff)
    assert isinstance(result, ChangelogScore)


def test_score_changelog_diff_sets_package_and_versions():
    diff = _make_diff(package="requests", old="2.0", new="3.0")
    result = score_changelog_diff(diff)
    assert result.package == "requests"
    assert result.old_version == "2.0"
    assert result.new_version == "3.0"


def test_score_changelog_diff_empty_lines_is_safe():
    diff = _make_diff(lines=[])
    result = score_changelog_diff(diff)
    assert result.score == 0
    assert result.risk_label == "safe"


def test_score_changelog_diff_breaking_line_increases_score():
    diff = _make_diff(lines=["Removed support for Python 2"])
    result = score_changelog_diff(diff)
    assert result.score > 0


def test_score_changelog_diff_line_count_matches():
    lines = ["Added feature X", "Removed old API", "Fixed bug Y"]
    diff = _make_diff(lines=lines)
    result = score_changelog_diff(diff)
    assert result.line_count == 3


def test_score_changelog_diff_severity_counts_dict():
    diff = _make_diff(lines=["Breaking change in config"])
    result = score_changelog_diff(diff)
    assert isinstance(result.severity_counts, dict)


# --- score_changelog_diffs ---

def test_score_changelog_diffs_sorted_descending():
    d1 = _make_diff(package="safe", lines=[])
    d2 = _make_diff(package="risky", lines=["Removed deprecated API", "Breaking change"])
    results = score_changelog_diffs([d1, d2])
    assert results[0].package == "risky"


def test_score_changelog_diffs_empty_list():
    assert score_changelog_diffs([]) == []


# --- top_risk_packages ---

def test_top_risk_packages_limits_results():
    diffs = [_make_diff(package=f"pkg{i}") for i in range(10)]
    scores = score_changelog_diffs(diffs)
    top = top_risk_packages(scores, n=3)
    assert len(top) <= 3


def test_top_risk_packages_default_n_is_five():
    diffs = [_make_diff(package=f"pkg{i}") for i in range(10)]
    scores = score_changelog_diffs(diffs)
    top = top_risk_packages(scores)
    assert len(top) <= 5
