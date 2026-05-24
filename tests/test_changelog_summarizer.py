"""Tests for depwatch.changelog_summarizer."""

import pytest

from depwatch.changelog_summarizer import (
    ChangelogSummary,
    build_changelog_summary,
    format_changelog_summary,
    _extract_bullet_points,
    _pick_headline,
)
from depwatch.severity_classifier import Severity


BREAKING_LINES = [
    "- Removed deprecated `foo()` API",
    "- Breaking change: config format updated",
    "- Renamed `bar` to `baz`",
]

SAFE_LINES = [
    "- Fixed a typo in the docs",
    "- Improved performance of internal loop",
]


def test_build_changelog_summary_returns_dataclass():
    result = build_changelog_summary("mylib", "1.0.0", "2.0.0", BREAKING_LINES)
    assert isinstance(result, ChangelogSummary)


def test_build_changelog_summary_sets_package_and_versions():
    result = build_changelog_summary("mylib", "1.0.0", "2.0.0", BREAKING_LINES)
    assert result.package == "mylib"
    assert result.from_version == "1.0.0"
    assert result.to_version == "2.0.0"


def test_build_changelog_summary_counts_total_lines():
    result = build_changelog_summary("mylib", "1.0.0", "2.0.0", BREAKING_LINES)
    assert result.total_lines == len(BREAKING_LINES)


def test_build_changelog_summary_detects_breaking():
    result = build_changelog_summary("mylib", "1.0.0", "2.0.0", BREAKING_LINES)
    assert result.breaking_count > 0


def test_build_changelog_summary_safe_lines_zero_breaking():
    result = build_changelog_summary("mylib", "1.0.0", "1.0.1", SAFE_LINES)
    assert result.breaking_count == 0


def test_build_changelog_summary_safe_severity_is_safe():
    result = build_changelog_summary("mylib", "1.0.0", "1.0.1", SAFE_LINES)
    assert result.highest_severity == Severity.SAFE


def test_build_changelog_summary_breaking_severity_not_safe():
    result = build_changelog_summary("mylib", "1.0.0", "2.0.0", BREAKING_LINES)
    assert result.highest_severity != Severity.SAFE


def test_build_changelog_summary_headline_contains_package():
    result = build_changelog_summary("mylib", "1.0.0", "2.0.0", BREAKING_LINES)
    assert "mylib" in result.headline


def test_build_changelog_summary_bullet_points_capped():
    many_lines = [f"- change number {i}" for i in range(20)]
    result = build_changelog_summary("pkg", "1.0", "2.0", many_lines, max_bullets=3)
    assert len(result.bullet_points) <= 3


def test_extract_bullet_points_strips_markers():
    lines = ["- first item", "* second item", "  plain line"]
    bullets = _extract_bullet_points(lines)
    assert all(not b.startswith("-") for b in bullets)
    assert all(not b.startswith("*") for b in bullets)


def test_extract_bullet_points_skips_empty():
    lines = ["", "  ", "- real line"]
    bullets = _extract_bullet_points(lines)
    assert bullets == ["real line"]


def test_pick_headline_format():
    headline = _pick_headline("requests", "2.0", "3.0", Severity.CRITICAL)
    assert "CRITICAL" in headline
    assert "requests" in headline
    assert "2.0" in headline
    assert "3.0" in headline


def test_format_changelog_summary_contains_headline():
    summary = build_changelog_summary("mylib", "1.0", "2.0", BREAKING_LINES)
    rendered = format_changelog_summary(summary)
    assert summary.headline in rendered


def test_format_changelog_summary_contains_breaking_count():
    summary = build_changelog_summary("mylib", "1.0", "2.0", BREAKING_LINES)
    rendered = format_changelog_summary(summary)
    assert str(summary.breaking_count) in rendered


def test_format_changelog_summary_contains_bullets():
    summary = build_changelog_summary("mylib", "1.0", "2.0", BREAKING_LINES)
    rendered = format_changelog_summary(summary)
    for bp in summary.bullet_points:
        assert bp in rendered
