"""Tests for depwatch.severity_report."""

import pytest
from depwatch.severity_classifier import Severity
from depwatch.severity_report import (
    SeverityReport,
    build_severity_report,
    format_severity_section,
)


# --- build_severity_report ---

def test_build_severity_report_returns_dataclass():
    report = build_severity_report("requests", "2.28.0", "2.29.0", [])
    assert isinstance(report, SeverityReport)


def test_build_severity_report_sets_package_and_versions():
    report = build_severity_report("requests", "2.28.0", "2.29.0", [])
    assert report.package == "requests"
    assert report.old_version == "2.28.0"
    assert report.new_version == "2.29.0"


def test_build_severity_report_empty_lines_is_safe():
    report = build_severity_report("requests", "2.28.0", "2.29.0", [])
    assert report.overall == Severity.SAFE
    assert report.annotated_lines == []


def test_build_severity_report_detects_critical():
    lines = ["removed the legacy auth method"]
    report = build_severity_report("mylib", "1.0", "2.0", lines)
    assert report.overall == Severity.CRITICAL


def test_build_severity_report_annotated_lines_count():
    lines = ["removed old API", "deprecated helper", "added new feature"]
    report = build_severity_report("mylib", "1.0", "2.0", lines)
    assert len(report.annotated_lines) == 3


def test_build_severity_report_annotated_line_severities():
    lines = ["removed old API", "deprecated helper"]
    report = build_severity_report("mylib", "1.0", "2.0", lines)
    severities = [s for _, s in report.annotated_lines]
    assert Severity.CRITICAL in severities
    assert Severity.HIGH in severities


# --- format_severity_section ---

def test_format_severity_section_contains_package_name():
    report = build_severity_report("requests", "2.28.0", "2.29.0", [])
    output = format_severity_section(report)
    assert "requests" in output


def test_format_severity_section_contains_versions():
    report = build_severity_report("requests", "2.28.0", "2.29.0", [])
    output = format_severity_section(report)
    assert "2.28.0" in output
    assert "2.29.0" in output


def test_format_severity_section_no_changes_message():
    report = build_severity_report("requests", "2.28.0", "2.29.0", [])
    output = format_severity_section(report)
    assert "No breaking changes detected" in output


def test_format_severity_section_has_table_header_when_changes():
    lines = ["removed old API"]
    report = build_severity_report("mylib", "1.0", "2.0", lines)
    output = format_severity_section(report)
    assert "| Severity | Change |" in output


def test_format_severity_section_contains_severity_label():
    lines = ["removed old API"]
    report = build_severity_report("mylib", "1.0", "2.0", lines)
    output = format_severity_section(report)
    assert "critical" in output


def test_format_severity_section_critical_emoji():
    lines = ["removed old API"]
    report = build_severity_report("mylib", "1.0", "2.0", lines)
    output = format_severity_section(report)
    assert "🔴" in output


def test_format_severity_section_safe_emoji_when_no_changes():
    report = build_severity_report("requests", "2.28.0", "2.29.0", [])
    output = format_severity_section(report)
    assert "🟢" in output
