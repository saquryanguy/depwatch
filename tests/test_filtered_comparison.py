"""Tests for filtered_comparison."""
import pytest
from depwatch.changelog_diff import ChangelogDiff
from depwatch.changelog_diff_comparator import compare_diffs, ComparisonReport
from depwatch.comparator_config import ComparatorConfig, config_from_dict
from depwatch.filtered_comparison import filter_comparison, format_comparison_markdown
from depwatch.severity_classifier import Severity


def _make_diff(package: str, lines: list) -> ChangelogDiff:
    return ChangelogDiff(package=package, old_version="1.0", new_version="2.0", lines=lines)


def _report() -> ComparisonReport:
    old = [_make_diff("requests", ["Breaking change: removed method"]), _make_diff("flask", [])]
    new = [_make_diff("requests", []), _make_diff("flask", ["Breaking change: api removed"])]
    return compare_diffs(old, new)


def test_filter_no_config_returns_all_entries():
    report = _report()
    cfg = ComparatorConfig()
    filtered = filter_comparison(report, cfg)
    assert len(filtered.entries) == 2


def test_filter_only_regressions():
    report = _report()
    cfg = ComparatorConfig(only_regressions=True)
    filtered = filter_comparison(report, cfg)
    assert all(e.regressed for e in filtered.entries)


def test_filter_ignore_packages():
    report = _report()
    cfg = ComparatorConfig(ignore_packages=["requests"])
    filtered = filter_comparison(report, cfg)
    assert all(e.package != "requests" for e in filtered.entries)


def test_filter_min_severity_excludes_safe():
    old = [_make_diff("pkg", [])]
    new = [_make_diff("pkg", [])]
    report = compare_diffs(old, new)
    cfg = ComparatorConfig(min_severity=Severity.HIGH)
    filtered = filter_comparison(report, cfg)
    assert filtered.entries == []


def test_config_from_dict_only_regressions_string():
    cfg = config_from_dict({"only_regressions": "true"})
    assert cfg.only_regressions is True


def test_config_from_dict_ignore_packages_string():
    cfg = config_from_dict({"ignore_packages": "requests, flask"})
    assert "requests" in cfg.ignore_packages
    assert "flask" in cfg.ignore_packages


def test_format_comparison_markdown_empty():
    report = ComparisonReport()
    md = format_comparison_markdown(report)
    assert "No changes" in md


def test_format_comparison_markdown_regressions():
    old = [_make_diff("requests", [])]
    new = [_make_diff("requests", ["Breaking change: removed method"])]
    report = compare_diffs(old, new)
    md = format_comparison_markdown(report)
    assert "Regressions" in md
    assert "requests" in md


def test_format_comparison_markdown_added_packages():
    report = ComparisonReport(packages_added=["newpkg"])
    md = format_comparison_markdown(report)
    assert "newpkg" in md
