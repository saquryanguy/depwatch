"""Tests for changelog_diff_deduplicator and dedup_config."""
from __future__ import annotations

import pytest

from depwatch.changelog_diff import ChangelogDiff
from depwatch.changelog_diff_deduplicator import (
    DeduplicatedDiff,
    DeduplicationReport,
    deduplicate_diff,
    deduplicate_diffs,
)
from depwatch.dedup_config import DedupConfig, config_from_dict, config_from_env


def _make_diff(package: str, lines: list[str]) -> ChangelogDiff:
    return ChangelogDiff(
        package=package,
        old_version="1.0.0",
        new_version="2.0.0",
        lines=lines,
    )


# --- deduplicate_diff ---

def test_deduplicate_diff_returns_dataclass():
    diff = _make_diff("requests", ["- removed foo"])
    result = deduplicate_diff(diff)
    assert isinstance(result, DeduplicatedDiff)


def test_deduplicate_diff_no_duplicates_unchanged():
    diff = _make_diff("requests", ["- removed foo", "- added bar"])
    result = deduplicate_diff(diff)
    assert result.deduplicated_count == 2
    assert result.removed_count == 0


def test_deduplicate_diff_removes_exact_duplicates():
    diff = _make_diff("requests", ["- removed foo", "- removed foo"])
    result = deduplicate_diff(diff)
    assert result.deduplicated_count == 1
    assert result.removed_count == 1


def test_deduplicate_diff_case_insensitive():
    diff = _make_diff("requests", ["- Removed Foo", "- removed foo"])
    result = deduplicate_diff(diff)
    assert result.removed_count == 1


def test_deduplicate_diff_strips_whitespace():
    diff = _make_diff("requests", ["  - removed foo  ", "- removed foo"])
    result = deduplicate_diff(diff)
    assert result.removed_count == 1


def test_deduplicate_diff_preserves_empty_lines():
    diff = _make_diff("requests", ["", "", "- removed foo"])
    result = deduplicate_diff(diff)
    # empty lines are kept as-is
    assert result.deduplicated_count == 3


def test_deduplicate_diff_package_preserved():
    diff = _make_diff("requests", ["- removed foo"])
    result = deduplicate_diff(diff)
    assert result.package == "requests"


def test_deduplicate_diff_original_count_correct():
    diff = _make_diff("requests", ["a", "b", "a"])
    result = deduplicate_diff(diff)
    assert result.original_count == 3


def test_deduplicate_diff_dedup_ratio():
    diff = _make_diff("requests", ["a", "a", "a", "b"])
    result = deduplicate_diff(diff)
    assert result.dedup_ratio == pytest.approx(0.5)


# --- deduplicate_diffs ---

def test_deduplicate_diffs_empty_returns_empty_report():
    report = deduplicate_diffs([])
    assert isinstance(report, DeduplicationReport)
    assert report.entries == []


def test_deduplicate_diffs_total_removed():
    d1 = _make_diff("requests", ["a", "a"])
    d2 = _make_diff("flask", ["b", "b", "b"])
    report = deduplicate_diffs([d1, d2])
    assert report.total_removed == 3


def test_deduplicate_diffs_packages():
    d1 = _make_diff("requests", ["a"])
    d2 = _make_diff("flask", ["b"])
    report = deduplicate_diffs([d1, d2])
    assert set(report.packages) == {"requests", "flask"}


def test_deduplicate_diffs_min_removed_filters():
    d1 = _make_diff("requests", ["a", "a"])  # removed=1
    d2 = _make_diff("flask", ["b"])           # removed=0
    report = deduplicate_diffs([d1, d2], min_removed=1)
    assert len(report.entries) == 1
    assert report.entries[0].package == "requests"


# --- config_from_dict ---

def test_config_from_dict_defaults():
    cfg = config_from_dict({})
    assert cfg.enabled is True
    assert cfg.min_removed == 0
    assert cfg.report_stats is False


def test_config_from_dict_disabled():
    cfg = config_from_dict({"enabled": "false"})
    assert cfg.enabled is False


def test_config_from_dict_min_removed():
    cfg = config_from_dict({"min_removed": 3})
    assert cfg.min_removed == 3


def test_config_from_dict_report_stats_true():
    cfg = config_from_dict({"report_stats": "true"})
    assert cfg.report_stats is True


def test_config_from_dict_invalid_min_removed_falls_back():
    cfg = config_from_dict({"min_removed": "bad"})
    assert cfg.min_removed == 0


# --- config_from_env ---

def test_config_from_env_defaults(monkeypatch):
    monkeypatch.delenv("DEPWATCH_DEDUP_ENABLED", raising=False)
    monkeypatch.delenv("DEPWATCH_DEDUP_MIN_REMOVED", raising=False)
    monkeypatch.delenv("DEPWATCH_DEDUP_REPORT_STATS", raising=False)
    cfg = config_from_env()
    assert cfg.enabled is True
    assert cfg.min_removed == 0
    assert cfg.report_stats is False


def test_config_from_env_disabled(monkeypatch):
    monkeypatch.setenv("DEPWATCH_DEDUP_ENABLED", "false")
    cfg = config_from_env()
    assert cfg.enabled is False


def test_config_from_env_min_removed(monkeypatch):
    monkeypatch.setenv("DEPWATCH_DEDUP_MIN_REMOVED", "5")
    cfg = config_from_env()
    assert cfg.min_removed == 5
