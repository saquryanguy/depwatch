"""Tests for depwatch.changelog_annotator."""

import pytest
from depwatch.changelog_annotator import (
    AnnotatedLine,
    annotate_line,
    annotate_lines,
    detect_categories,
    filter_annotated,
)
from depwatch.severity_classifier import Severity


# ---------------------------------------------------------------------------
# detect_categories
# ---------------------------------------------------------------------------

def test_detect_categories_security():
    cats = detect_categories("Fixed CVE-2024-1234 vulnerability")
    assert "security" in cats


def test_detect_categories_api():
    cats = detect_categories("Changed the public API signature")
    assert "api" in cats


def test_detect_categories_multiple():
    cats = detect_categories("Security patch changes API endpoint behavior")
    assert "security" in cats
    assert "api" in cats


def test_detect_categories_none():
    cats = detect_categories("Minor internal refactor")
    assert cats == []


# ---------------------------------------------------------------------------
# annotate_line
# ---------------------------------------------------------------------------

def test_annotate_line_returns_dataclass():
    al = annotate_line("Removed deprecated function")
    assert isinstance(al, AnnotatedLine)


def test_annotate_line_sets_text():
    al = annotate_line("Breaking change in scheduler")
    assert al.text == "Breaking change in scheduler"


def test_annotate_line_sets_severity():
    al = annotate_line("Breaking change in scheduler")
    assert al.severity == Severity.CRITICAL


def test_annotate_line_sets_line_number():
    al = annotate_line("Some change", line_number=7)
    assert al.line_number == 7


def test_annotate_line_no_line_number_defaults_none():
    al = annotate_line("Some change")
    assert al.line_number is None


# ---------------------------------------------------------------------------
# annotate_lines
# ---------------------------------------------------------------------------

def test_annotate_lines_count():
    lines = ["Breaking change", "Minor fix", "Removed old API"]
    result = annotate_lines(lines)
    assert len(result) == 3


def test_annotate_lines_line_numbers_are_one_indexed():
    lines = ["first", "second"]
    result = annotate_lines(lines)
    assert result[0].line_number == 1
    assert result[1].line_number == 2


# ---------------------------------------------------------------------------
# filter_annotated
# ---------------------------------------------------------------------------

def test_filter_annotated_min_severity_excludes_low():
    lines = ["Minor tweak", "Breaking change removed"]
    annotated = annotate_lines(lines)
    result = filter_annotated(annotated, min_severity=Severity.HIGH)
    severities = {al.severity for al in result}
    assert Severity.LOW not in severities


def test_filter_annotated_by_category():
    lines = ["Fixed CVE-2024-1234 security issue", "Breaking change in API"]
    annotated = annotate_lines(lines)
    result = filter_annotated(annotated, categories=["security"])
    assert all("security" in al.categories for al in result)


def test_filter_annotated_no_category_filter_returns_all_above_min():
    lines = ["Breaking change", "Deprecated method", "Minor note"]
    annotated = annotate_lines(lines)
    result = filter_annotated(annotated, min_severity=Severity.LOW)
    assert len(result) == len(annotated)
