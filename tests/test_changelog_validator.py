"""Tests for depwatch.changelog_validator."""
import pytest

from depwatch.changelog_validator import (
    ValidationResult,
    validate_changelog,
    validate_changelogs,
    _check_has_version_headers,
    _check_min_length,
)


MINIMAL_CHANGELOG = """# 1.2.0
- Added something
- Fixed a bug
"""

HEADERLESS_CHANGELOG = "Added something\nFixed a bug\nChanged behaviour\n"


def test_validate_changelog_returns_dataclass():
    result = validate_changelog("mypkg", MINIMAL_CHANGELOG)
    assert isinstance(result, ValidationResult)


def test_validate_changelog_sets_package():
    result = validate_changelog("mypkg", MINIMAL_CHANGELOG)
    assert result.package == "mypkg"


def test_validate_changelog_valid_content_is_valid():
    result = validate_changelog("mypkg", MINIMAL_CHANGELOG)
    assert result.is_valid is True
    assert not result.has_errors


def test_validate_changelog_none_content_is_invalid():
    result = validate_changelog("mypkg", None)
    assert result.is_valid is False
    assert result.has_errors


def test_validate_changelog_empty_string_is_invalid():
    result = validate_changelog("mypkg", "")
    assert result.is_valid is False


def test_validate_changelog_empty_string_error_message():
    result = validate_changelog("mypkg", "")
    assert any("empty" in e.lower() for e in result.errors)


def test_validate_changelog_no_version_headers_adds_warning():
    result = validate_changelog("mypkg", HEADERLESS_CHANGELOG)
    assert result.has_warnings
    assert any("header" in w.lower() for w in result.warnings)


def test_validate_changelog_too_short_adds_warning():
    result = validate_changelog("mypkg", "# 1.0.0\nOne line\n", min_lines=5)
    assert result.has_warnings
    assert any("short" in w.lower() for w in result.warnings)


def test_validate_changelog_valid_has_no_warnings_on_good_input():
    result = validate_changelog("mypkg", MINIMAL_CHANGELOG)
    assert not result.has_warnings


def test_check_has_version_headers_with_hash():
    lines = ["# 1.0.0", "- change"]
    assert _check_has_version_headers(lines) is None


def test_check_has_version_headers_with_bracket():
    lines = ["[1.0.0]", "- change"]
    assert _check_has_version_headers(lines) is None


def test_check_has_version_headers_missing_returns_string():
    lines = ["just text", "no headers here"]
    result = _check_has_version_headers(lines)
    assert isinstance(result, str)


def test_check_min_length_sufficient():
    lines = ["a", "b", "c"]
    assert _check_min_length(lines, 3) is None


def test_check_min_length_insufficient():
    lines = ["a", "b"]
    result = _check_min_length(lines, 3)
    assert isinstance(result, str)


def test_validate_changelogs_returns_list():
    changelogs = {"pkgA": MINIMAL_CHANGELOG, "pkgB": None}
    results = validate_changelogs(changelogs)
    assert len(results) == 2


def test_validate_changelogs_correct_packages():
    changelogs = {"pkgA": MINIMAL_CHANGELOG, "pkgB": MINIMAL_CHANGELOG}
    results = validate_changelogs(changelogs)
    packages = {r.package for r in results}
    assert packages == {"pkgA", "pkgB"}


def test_validate_changelogs_invalid_entry_detected():
    changelogs = {"good": MINIMAL_CHANGELOG, "bad": ""}
    results = validate_changelogs(changelogs)
    bad = next(r for r in results if r.package == "bad")
    assert not bad.is_valid
