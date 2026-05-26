"""Tests for changelog_diff_tagger."""
from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from depwatch.changelog_diff import ChangelogDiff
from depwatch.changelog_diff_tagger import (
    TaggedDiff,
    TaggerReport,
    tag_diff,
    tag_diffs,
)
from depwatch.severity_classifier import Severity


def _make_diff(package: str = "mypkg", lines=None) -> ChangelogDiff:
    diff = MagicMock(spec=ChangelogDiff)
    diff.package = package
    diff.lines = lines or []
    return diff


def test_tag_diff_returns_tagged_diff():
    diff = _make_diff()
    result = tag_diff(diff)
    assert isinstance(result, TaggedDiff)


def test_tag_diff_sets_package():
    diff = _make_diff(package="requests")
    result = tag_diff(diff)
    assert result.package == "requests"


def test_tag_diff_safe_when_no_lines():
    diff = _make_diff(lines=[])
    result = tag_diff(diff)
    assert result.severity == Severity.SAFE
    assert "safe" in result.tags


def test_tag_diff_breaking_line_gets_breaking_tag():
    diff = _make_diff(lines=["- Removed `foo()` API"])
    result = tag_diff(diff)
    assert result.severity != Severity.SAFE
    assert any(t in result.tags for t in ("breaking", "high-risk", "api-change"))


def test_tag_diff_security_keyword_adds_security_tag():
    diff = _make_diff(lines=["Fixed a security vulnerability CVE-2024-1234"])
    result = tag_diff(diff)
    assert "security" in result.tags


def test_tag_diff_deprecation_keyword_adds_deprecation_tag():
    diff = _make_diff(lines=["The old API is deprecated and will be removed."])
    result = tag_diff(diff)
    assert "deprecation" in result.tags


def test_tag_diff_extra_tags_are_appended():
    diff = _make_diff()
    result = tag_diff(diff, extra_tags=["custom-tag"])
    assert "custom-tag" in result.tags


def test_tag_diff_no_duplicate_tags():
    diff = _make_diff(lines=["Removed foo", "Removed bar"])
    result = tag_diff(diff, extra_tags=["safe"])
    assert len(result.tags) == len(set(result.tags))


def test_tagged_diff_is_tagged_true_when_tags_present():
    diff = _make_diff()
    td = TaggedDiff(diff=diff, tags=["breaking"], severity=Severity.CRITICAL)
    assert td.is_tagged is True


def test_tagged_diff_is_tagged_false_when_no_tags():
    diff = _make_diff()
    td = TaggedDiff(diff=diff, tags=[], severity=Severity.SAFE)
    assert td.is_tagged is False


def test_tag_diffs_returns_tagger_report():
    diffs = [_make_diff("pkg1"), _make_diff("pkg2")]
    report = tag_diffs(diffs)
    assert isinstance(report, TaggerReport)
    assert report.total == 2


def test_tagger_report_tagged_count():
    diff1 = _make_diff(lines=["Removed foo"])
    diff2 = _make_diff(lines=[])
    report = tag_diffs([diff1, diff2])
    assert report.tagged_count >= 1


def test_tag_diffs_empty_input():
    report = tag_diffs([])
    assert report.total == 0
    assert report.tagged_count == 0
