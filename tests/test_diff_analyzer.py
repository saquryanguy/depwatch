"""Tests for depwatch.diff_analyzer."""

import pytest
from depwatch.diff_analyzer import (
    is_breaking_line,
    extract_breaking_changes,
    summarize_breaking_changes,
)


def test_is_breaking_line_detects_breaking():
    assert is_breaking_line("Breaking: removed support for Python 3.7") is True


def test_is_breaking_line_detects_removed():
    assert is_breaking_line("Removed the legacy API endpoint") is True


def test_is_breaking_line_detects_deprecated():
    assert is_breaking_line("Deprecated `old_func`, use `new_func` instead") is True


def test_is_breaking_line_safe_line():
    assert is_breaking_line("Added support for async context managers") is False


def test_is_breaking_line_empty():
    assert is_breaking_line("") is False


def test_extract_breaking_changes_finds_versions():
    sections = {
        "1.2.0": "Added new feature\nBreaking: renamed `foo` to `bar`",
        "1.1.0": "Fixed a bug\nImproved performance",
    }
    result = extract_breaking_changes(sections)
    assert "1.2.0" in result
    assert "1.1.0" not in result


def test_extract_breaking_changes_content():
    sections = {"2.0.0": "Removed deprecated methods\nAdded new API"}
    result = extract_breaking_changes(sections)
    assert any("Removed" in line for line in result["2.0.0"])


def test_extract_breaking_changes_empty_sections():
    assert extract_breaking_changes({}) == {}


def test_summarize_breaking_changes_no_breaking():
    result = summarize_breaking_changes({})
    assert result == "No breaking changes detected."


def test_summarize_breaking_changes_with_data():
    breaking = {"2.0.0": ["Breaking: removed `old_api`"]}
    result = summarize_breaking_changes(breaking)
    assert "2.0.0" in result
    assert "Breaking" in result
    assert "⚠️" in result


def test_summarize_breaking_changes_multiple_versions():
    breaking = {
        "3.0.0": ["Removed Python 2 support"],
        "2.5.0": ["Deprecated legacy auth"],
    }
    result = summarize_breaking_changes(breaking)
    assert "3.0.0" in result
    assert "2.5.0" in result
