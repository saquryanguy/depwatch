"""Tests for changelog_diff_archiver and archive_config."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from depwatch.changelog_diff import ChangelogDiff
from depwatch.changelog_diff_archiver import (
    ArchiveEntry,
    ArchiveResult,
    archive_diff,
    archive_diffs,
    load_archive_entry,
)
from depwatch.archive_config import ArchiveConfig, config_from_dict, config_from_env


def _make_diff(package="requests", old="2.28.0", new="2.29.0",
               lines=None) -> ChangelogDiff:
    return ChangelogDiff(
        package=package,
        old_version=old,
        new_version=new,
        lines=lines or ["- removed legacy auth"],
    )


@pytest.fixture()
def tmp_archive(tmp_path):
    return str(tmp_path / "archive")


def test_archive_diff_creates_file(tmp_archive):
    diff = _make_diff()
    result = archive_diff(diff, archive_dir=tmp_archive)
    assert result.success
    assert Path(result.path).exists()


def test_archive_diff_result_package(tmp_archive):
    diff = _make_diff(package="flask")
    result = archive_diff(diff, archive_dir=tmp_archive)
    assert result.package == "flask"


def test_archive_diff_json_content(tmp_archive):
    diff = _make_diff(lines=["breaking: removed foo"])
    result = archive_diff(diff, archive_dir=tmp_archive)
    data = json.loads(Path(result.path).read_text())
    assert data["lines"] == ["breaking: removed foo"]
    assert data["old_version"] == "2.28.0"


def test_archive_diff_uses_run_id_in_filename(tmp_archive):
    diff = _make_diff()
    result = archive_diff(diff, archive_dir=tmp_archive, run_id="run-42")
    assert "run-42" in result.path


def test_archive_diffs_returns_one_per_diff(tmp_archive):
    diffs = [_make_diff("pkg-a"), _make_diff("pkg-b")]
    results = archive_diffs(diffs, archive_dir=tmp_archive)
    assert len(results) == 2
    assert all(r.success for r in results)


def test_load_archive_entry_roundtrip(tmp_archive):
    diff = _make_diff()
    result = archive_diff(diff, archive_dir=tmp_archive)
    entry = load_archive_entry(result.path)
    assert isinstance(entry, ArchiveEntry)
    assert entry.package == "requests"
    assert entry.old_version == "2.28.0"


def test_load_archive_entry_missing_returns_none(tmp_path):
    assert load_archive_entry(str(tmp_path / "ghost.json")) is None


def test_config_from_dict_defaults():
    cfg = config_from_dict({})
    assert cfg.enabled is True
    assert cfg.run_id is None


def test_config_from_dict_disabled():
    cfg = config_from_dict({"enabled": "false"})
    assert cfg.enabled is False


def test_config_from_dict_sets_run_id():
    cfg = config_from_dict({"run_id": "abc123"})
    assert cfg.run_id == "abc123"


def test_config_from_env_defaults(monkeypatch):
    monkeypatch.delenv("DEPWATCH_ARCHIVE_ENABLED", raising=False)
    monkeypatch.delenv("DEPWATCH_ARCHIVE_DIR", raising=False)
    monkeypatch.delenv("DEPWATCH_RUN_ID", raising=False)
    cfg = config_from_env()
    assert cfg.enabled is True
    assert cfg.run_id is None
