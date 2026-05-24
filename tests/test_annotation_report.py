"""Tests for depwatch.annotation_report."""

import pytest
from depwatch.annotation_report import (
    AnnotationReport,
    build_annotation_report,
    format_annotation_report,
)
from depwatch.severity_classifier import Severity


SAMPLE_LINES = [
    "Breaking change: removed legacy auth module",
    "Deprecated old config format",
    "Fixed CVE-2024-9999 security vulnerability",
    "Minor internal cleanup",
]


# ---------------------------------------------------------------------------
# build_annotation_report
# ---------------------------------------------------------------------------

def test_build_annotation_report_returns_dataclass():
    report = build_annotation_report("requests", "2.28.0", "2.29.0", SAMPLE_LINES)
    assert isinstance(report, AnnotationReport)


def test_build_annotation_report_sets_package():
    report = build_annotation_report("requests", "2.28.0", "2.29.0", SAMPLE_LINES)
    assert report.package == "requests"


def test_build_annotation_report_sets_versions():
    report = build_annotation_report("requests", "2.28.0", "2.29.0", SAMPLE_LINES)
    assert report.old_version == "2.28.0"
    assert report.new_version == "2.29.0"


def test_build_annotation_report_annotates_all_lines_default():
    report = build_annotation_report("pkg", "1.0", "2.0", SAMPLE_LINES)
    assert len(report.annotated_lines) == len(SAMPLE_LINES)


def test_build_annotation_report_highest_severity_critical():
    report = build_annotation_report("pkg", "1.0", "2.0", SAMPLE_LINES)
    assert report.highest_severity == Severity.CRITICAL


def test_build_annotation_report_empty_lines_is_safe():
    report = build_annotation_report("pkg", "1.0", "1.1", [])
    assert report.highest_severity == Severity.LOW
    assert report.annotated_lines == []


def test_build_annotation_report_min_severity_filters():
    report = build_annotation_report(
        "pkg", "1.0", "2.0", SAMPLE_LINES, min_severity=Severity.HIGH
    )
    for al in report.annotated_lines:
        assert al.severity in (Severity.HIGH, Severity.CRITICAL)


def test_build_annotation_report_category_counts_populated():
    report = build_annotation_report("pkg", "1.0", "2.0", SAMPLE_LINES)
    assert "security" in report.category_counts
    assert report.category_counts["security"] >= 1


def test_build_annotation_report_category_filter():
    report = build_annotation_report(
        "pkg", "1.0", "2.0", SAMPLE_LINES, categories=["security"]
    )
    for al in report.annotated_lines:
        assert "security" in al.categories


# ---------------------------------------------------------------------------
# format_annotation_report
# ---------------------------------------------------------------------------

def test_format_annotation_report_contains_package():
    report = build_annotation_report("requests", "2.28.0", "2.29.0", SAMPLE_LINES)
    text = format_annotation_report(report)
    assert "requests" in text


def test_format_annotation_report_contains_versions():
    report = build_annotation_report("requests", "2.28.0", "2.29.0", SAMPLE_LINES)
    text = format_annotation_report(report)
    assert "2.28.0" in text
    assert "2.29.0" in text


def test_format_annotation_report_contains_severity():
    report = build_annotation_report("pkg", "1.0", "2.0", SAMPLE_LINES)
    text = format_annotation_report(report)
    assert "CRITICAL" in text or "critical" in text.lower()


def test_format_annotation_report_empty_shows_no_changes():
    report = build_annotation_report("pkg", "1.0", "1.1", [])
    text = format_annotation_report(report)
    assert "No notable changes" in text
