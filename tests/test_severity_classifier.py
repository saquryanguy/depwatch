"""Tests for depwatch.severity_classifier."""

import pytest
from depwatch.severity_classifier import (
    Severity,
    classify_line,
    classify_changes,
    highest_severity,
)


# --- classify_line ---

def test_classify_line_critical_removed():
    assert classify_line("The `foo` function has been removed.") == Severity.CRITICAL


def test_classify_line_critical_breaking_change():
    assert classify_line("Breaking change: auth flow updated") == Severity.CRITICAL


def test_classify_line_critical_case_insensitive():
    assert classify_line("REMOVED the legacy endpoint") == Severity.CRITICAL


def test_classify_line_high_deprecated():
    assert classify_line("Deprecated: use new_func instead") == Severity.HIGH


def test_classify_line_high_renamed():
    assert classify_line("Config key renamed to `new_key`") == Severity.HIGH


def test_classify_line_medium_changed_default():
    assert classify_line("Changed default timeout from 30 to 60") == Severity.MEDIUM


def test_classify_line_medium_now_raises():
    assert classify_line("now raises ValueError on bad input") == Severity.MEDIUM


def test_classify_line_low_warning():
    assert classify_line("Warning: this may change in future") == Severity.LOW


def test_classify_line_safe():
    assert classify_line("Added support for Python 3.12") == Severity.SAFE


def test_classify_line_empty_is_safe():
    assert classify_line("") == Severity.SAFE


# --- classify_changes ---

def test_classify_changes_returns_pairs():
    lines = ["removed old API", "added new feature"]
    result = classify_changes(lines)
    assert len(result) == 2
    assert result[0] == ("removed old API", Severity.CRITICAL)
    assert result[1] == ("added new feature", Severity.SAFE)


def test_classify_changes_skips_blank_lines():
    lines = ["removed old API", "", "   ", "added new feature"]
    result = classify_changes(lines)
    assert len(result) == 2


# --- highest_severity ---

def test_highest_severity_returns_critical_when_present():
    lines = ["deprecated old func", "removed legacy method"]
    assert highest_severity(lines) == Severity.CRITICAL


def test_highest_severity_returns_high_without_critical():
    lines = ["deprecated old func", "added new helper"]
    assert highest_severity(lines) == Severity.HIGH


def test_highest_severity_all_safe():
    lines = ["added support for Python 3.12", "fixed typo in docs"]
    assert highest_severity(lines) == Severity.SAFE


def test_highest_severity_empty_list():
    assert highest_severity([]) == Severity.SAFE


def test_highest_severity_only_blank_lines():
    assert highest_severity(["", "   "]) == Severity.SAFE
