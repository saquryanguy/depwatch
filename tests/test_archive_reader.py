"""Tests for archive_reader."""
from __future__ import annotations

import pytest

from depwatch.changelog_diff import ChangelogDiff
from depwatch.changelog_diff_archiver import archive_diff
from depwatch.archive_reader import (
    entries_for_package,
    latest_entry,
    list_archive_files,
    load_all_entries,
)


def _make_diff(package="requests", old="2.28.0", new="2.29.0") -> ChangelogDiff:
    return ChangelogDiff(package=package, old_version=old, new_version=new,
                         lines=["- change"])


@pytest.fixture()
def populated_archive(tmp_path):
    d = str(tmp_path / "archive")
    archive_diff(_make_diff("requests"), archive_dir=d, run_id="run-01")
    archive_diff(_make_diff("requests", new="2.30.0"), archive_dir=d, run_id="run-02")
    archive_diff(_make_diff("flask"), archive_dir=d, run_id="run-01")
    return d


def test_list_archive_files_empty(tmp_path):
    assert list_archive_files(str(tmp_path / "missing")) == []


def test_list_archive_files_count(populated_archive):
    files = list_archive_files(populated_archive)
    assert len(files) == 3


def test_load_all_entries_count(populated_archive):
    entries = load_all_entries(populated_archive)
    assert len(entries) == 3


def test_load_all_entries_empty_dir(tmp_path):
    assert load_all_entries(str(tmp_path / "empty")) == []


def test_entries_for_package_filters_correctly(populated_archive):
    results = entries_for_package(populated_archive, "requests")
    assert len(results) == 2
    assert all(e.package == "requests" for e in results)


def test_entries_for_package_normalises_name(populated_archive):
    # archive stores 'flask', query with 'Flask'
    results = entries_for_package(populated_archive, "Flask")
    assert len(results) == 1


def test_entries_for_package_unknown_returns_empty(populated_archive):
    assert entries_for_package(populated_archive, "nonexistent") == []


def test_latest_entry_returns_last(populated_archive):
    entry = latest_entry(populated_archive, "requests")
    assert entry is not None
    assert entry.new_version == "2.30.0"


def test_latest_entry_missing_package_returns_none(populated_archive):
    assert latest_entry(populated_archive, "django") is None
