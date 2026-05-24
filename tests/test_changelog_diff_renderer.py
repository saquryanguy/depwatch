"""Tests for changelog_diff_renderer and rendered_diff_report."""
from __future__ import annotations

import pytest

from depwatch.changelog_diff import ChangelogDiff
from depwatch.changelog_diff_renderer import RenderedDiff, render_diff, render_diffs
from depwatch.diff_render_config import DiffRenderConfig, config_from_dict
from depwatch.rendered_diff_report import (
    RenderedDiffReport,
    build_rendered_diff_report,
    format_rendered_diff_report,
)
from depwatch.severity_classifier import Severity


def _make_diff(package="requests", old="1.0", new="2.0", lines=None):
    return ChangelogDiff(
        package=package,
        old_version=old,
        new_version=new,
        lines=lines or [],
    )


# --- render_diff ---

def test_render_diff_returns_rendered_diff():
    diff = _make_diff(lines=["Added new feature"])
    result = render_diff(diff)
    assert isinstance(result, RenderedDiff)


def test_render_diff_sets_package_and_versions():
    diff = _make_diff(package="flask", old="0.9", new="1.0")
    result = render_diff(diff)
    assert result.package == "flask"
    assert result.old_version == "0.9"
    assert result.new_version == "1.0"


def test_render_diff_safe_when_no_breaking_lines():
    diff = _make_diff(lines=["Added new helper", "Improved docs"])
    result = render_diff(diff)
    assert result.severity == Severity.SAFE


def test_render_diff_critical_for_breaking_change():
    diff = _make_diff(lines=["Removed support for Python 2", "Breaking change in API"])
    result = render_diff(diff)
    assert result.severity in (Severity.CRITICAL, Severity.HIGH)


def test_render_diff_markdown_contains_package():
    diff = _make_diff(package="boto3")
    result = render_diff(diff)
    assert "boto3" in result.markdown


def test_render_diff_plain_contains_arrow():
    diff = _make_diff(old="1.0", new="2.0")
    result = render_diff(diff)
    assert "->" in result.plain


def test_render_diff_empty_lines_shows_no_content_message():
    diff = _make_diff(lines=[])
    result = render_diff(diff)
    assert "No changelog" in result.markdown


# --- render_diffs ---

def test_render_diffs_returns_all_by_default():
    diffs = [_make_diff("pkg1"), _make_diff("pkg2")]
    results = render_diffs(diffs)
    assert len(results) == 2


def test_render_diffs_filters_by_min_severity():
    safe_diff = _make_diff("safe-pkg", lines=["Minor doc update"])
    risky_diff = _make_diff("risky-pkg", lines=["Removed deprecated API"])
    results = render_diffs([safe_diff, risky_diff], min_severity=Severity.HIGH)
    packages = [r.package for r in results]
    assert "risky-pkg" in packages


# --- build_rendered_diff_report ---

def test_build_rendered_diff_report_empty_diffs():
    report = build_rendered_diff_report([])
    assert isinstance(report, RenderedDiffReport)
    assert report.total_packages == 0
    assert report.is_clean()


def test_build_rendered_diff_report_counts_packages():
    diffs = [_make_diff("a"), _make_diff("b"), _make_diff("c")]
    report = build_rendered_diff_report(diffs)
    assert report.total_packages == 3


def test_build_rendered_diff_report_counts_risky():
    diffs = [
        _make_diff("safe", lines=["Added helper"]),
        _make_diff("risky", lines=["Removed old method"]),
    ]
    report = build_rendered_diff_report(diffs)
    assert report.risky_packages >= 1


def test_build_rendered_diff_report_truncates_lines():
    long_lines = [f"line {i}" for i in range(100)]
    diff = _make_diff(lines=long_lines)
    config = DiffRenderConfig(max_lines_per_package=10)
    report = build_rendered_diff_report([diff], config=config)
    assert len(report.entries[0].lines) == 10


# --- format_rendered_diff_report ---

def test_format_rendered_diff_report_empty_returns_message():
    report = RenderedDiffReport()
    output = format_rendered_diff_report(report)
    assert "No dependency" in output


def test_format_rendered_diff_report_markdown_default():
    diffs = [_make_diff("mylib", lines=["Fixed bug"])]
    report = build_rendered_diff_report(diffs)
    output = format_rendered_diff_report(report, output_format="markdown")
    assert "mylib" in output
    assert "###" in output


def test_format_rendered_diff_report_plain():
    diffs = [_make_diff("mylib", lines=["Fixed bug"])]
    report = build_rendered_diff_report(diffs)
    output = format_rendered_diff_report(report, output_format="plain")
    assert "mylib" in output
    assert "###" not in output
