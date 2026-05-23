"""Tests for depwatch.filter_engine."""

import pytest

from depwatch.filter_engine import (
    FilterCriteria,
    apply_filter,
    filter_lines,
    matches_keywords,
    matches_package,
    matches_severity,
)
from depwatch.severity_classifier import Severity

# ---------------------------------------------------------------------------
# matches_severity
# ---------------------------------------------------------------------------

def test_matches_severity_equal():
    assert matches_severity(Severity.HIGH, Severity.HIGH) is True


def test_matches_severity_above_min():
    assert matches_severity(Severity.CRITICAL, Severity.HIGH) is True


def test_matches_severity_below_min():
    assert matches_severity(Severity.LOW, Severity.HIGH) is False


# ---------------------------------------------------------------------------
# matches_package
# ---------------------------------------------------------------------------

def test_matches_package_empty_allowed_returns_true():
    assert matches_package("requests", []) is True


def test_matches_package_found():
    assert matches_package("requests", ["requests", "flask"]) is True


def test_matches_package_not_found():
    assert matches_package("django", ["requests", "flask"]) is False


def test_matches_package_case_insensitive():
    assert matches_package("Requests", ["requests"]) is True


def test_matches_package_normalizes_hyphens():
    assert matches_package("my-package", ["my_package"]) is True


# ---------------------------------------------------------------------------
# matches_keywords
# ---------------------------------------------------------------------------

def test_matches_keywords_empty_returns_true():
    assert matches_keywords("some line", []) is True


def test_matches_keywords_found():
    assert matches_keywords("Removed deprecated API", ["deprecated"]) is True


def test_matches_keywords_not_found():
    assert matches_keywords("minor bugfix", ["breaking"]) is False


def test_matches_keywords_case_insensitive():
    assert matches_keywords("BREAKING CHANGE", ["breaking"]) is True


def test_matches_keywords_multiple_all_absent():
    assert matches_keywords("minor fix", ["breaking", "deprecated"]) is False


def test_matches_keywords_multiple_one_present():
    assert matches_keywords("deprecated function removed", ["breaking", "deprecated"]) is True


# ---------------------------------------------------------------------------
# filter_lines
# ---------------------------------------------------------------------------

_LINES = ["removed old api", "minor fix", "deprecated helper"]
_ANNOTATED = [
    ("removed old api", Severity.CRITICAL),
    ("minor fix", Severity.LOW),
    ("deprecated helper", Severity.HIGH),
]


def test_filter_lines_min_severity_high():
    criteria = FilterCriteria(min_severity=Severity.HIGH)
    result = filter_lines(_LINES, _ANNOTATED, criteria)
    assert result == ["removed old api", "deprecated helper"]


def test_filter_lines_keyword_filter():
    criteria = FilterCriteria(min_severity=Severity.LOW, keywords=["removed"])
    result = filter_lines(_LINES, _ANNOTATED, criteria)
    assert result == ["removed old api"]


def test_filter_lines_length_mismatch_raises():
    with pytest.raises(ValueError):
        filter_lines(_LINES, _ANNOTATED[:2], FilterCriteria())
