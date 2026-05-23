"""Tests for depwatch.changelog_diff."""

from unittest.mock import patch

import pytest

from depwatch.changelog_diff import (
    ChangelogDiff,
    fetch_changelog_diff,
    fetch_changelog_diffs,
)

SAMPLE_CHANGELOG = """
## 2.0.0
- Breaking: removed old API
- Added new interface

## 1.5.0
- Deprecated legacy helper
- Fixed bug in parser

## 1.0.0
- Initial release
"""


@pytest.fixture()
def patched_changelog():
    with patch(
        "depwatch.changelog_diff.cached_get_changelog",
        return_value=SAMPLE_CHANGELOG,
    ) as mock:
        yield mock


@pytest.fixture()
def no_changelog():
    with patch(
        "depwatch.changelog_diff.cached_get_changelog",
        return_value=None,
    ) as mock:
        yield mock


def test_fetch_changelog_diff_returns_dataclass(patched_changelog):
    result = fetch_changelog_diff("mypkg", "1.5.0", "2.0.0")
    assert isinstance(result, ChangelogDiff)


def test_fetch_changelog_diff_sets_package(patched_changelog):
    result = fetch_changelog_diff("mypkg", "1.5.0", "2.0.0")
    assert result.package == "mypkg"


def test_fetch_changelog_diff_sets_versions(patched_changelog):
    result = fetch_changelog_diff("mypkg", "1.5.0", "2.0.0")
    assert result.old_version == "1.5.0"
    assert result.new_version == "2.0.0"


def test_fetch_changelog_diff_found_when_changelog_exists(patched_changelog):
    result = fetch_changelog_diff("mypkg", "1.5.0", "2.0.0")
    assert result.found is True
    assert result.error is None


def test_fetch_changelog_diff_error_when_no_changelog(no_changelog):
    result = fetch_changelog_diff("mypkg", "1.0.0", "2.0.0")
    assert result.found is False
    assert result.error is not None
    assert "mypkg" in result.error


def test_fetch_changelog_diff_empty_when_no_changelog(no_changelog):
    result = fetch_changelog_diff("mypkg", "1.0.0", "2.0.0")
    assert result.is_empty is True


def test_fetch_changelog_diff_lines_not_empty(patched_changelog):
    with patch(
        "depwatch.changelog_diff.extract_sections_between",
        return_value=["- Breaking: removed old API", "- Added new interface"],
    ):
        result = fetch_changelog_diff("mypkg", "1.5.0", "2.0.0")
        assert result.is_empty is False
        assert len(result.lines) == 2


def test_fetch_changelog_diffs_returns_list(patched_changelog):
    upgrades = {"mypkg": ("1.5.0", "2.0.0"), "otherpkg": ("0.9.0", "1.0.0")}
    results = fetch_changelog_diffs(upgrades)
    assert len(results) == 2


def test_fetch_changelog_diffs_preserves_package_names(patched_changelog):
    upgrades = {"alpha": ("1.0.0", "2.0.0"), "beta": ("0.1.0", "0.2.0")}
    results = fetch_changelog_diffs(upgrades)
    names = {r.package for r in results}
    assert names == {"alpha", "beta"}


def test_fetch_changelog_diffs_empty_upgrades(patched_changelog):
    results = fetch_changelog_diffs({})
    assert results == []
