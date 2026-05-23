"""Tests for depwatch.baseline_store."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from depwatch.baseline_store import (
    diff_from_baseline,
    load_baseline,
    save_baseline,
)


@pytest.fixture()
def tmp_baseline(tmp_path: Path) -> Path:
    return tmp_path / "baseline.json"


def test_load_baseline_missing_returns_empty(tmp_baseline: Path) -> None:
    assert load_baseline(tmp_baseline) == {}


def test_save_and_load_roundtrip(tmp_baseline: Path) -> None:
    deps = {"requests": "2.31.0", "flask": "3.0.1"}
    save_baseline(deps, tmp_baseline)
    assert load_baseline(tmp_baseline) == deps


def test_save_overwrites_existing(tmp_baseline: Path) -> None:
    save_baseline({"requests": "2.28.0"}, tmp_baseline)
    save_baseline({"requests": "2.31.0"}, tmp_baseline)
    assert load_baseline(tmp_baseline) == {"requests": "2.31.0"}


def test_load_baseline_invalid_json_returns_empty(tmp_baseline: Path) -> None:
    tmp_baseline.write_text("not json", encoding="utf-8")
    assert load_baseline(tmp_baseline) == {}


def test_load_baseline_non_dict_json_returns_empty(tmp_baseline: Path) -> None:
    tmp_baseline.write_text(json.dumps([1, 2, 3]), encoding="utf-8")
    assert load_baseline(tmp_baseline) == {}


def test_save_creates_parent_directories(tmp_path: Path) -> None:
    deep = tmp_path / "a" / "b" / "baseline.json"
    save_baseline({"pkg": "1.0.0"}, deep)
    assert deep.exists()


def test_diff_from_baseline_detects_upgrade(tmp_baseline: Path) -> None:
    save_baseline({"requests": "2.28.0"}, tmp_baseline)
    result = diff_from_baseline({"requests": "2.31.0"}, path=tmp_baseline)
    assert result == {"requests": ("2.28.0", "2.31.0")}


def test_diff_from_baseline_new_package_has_empty_old(tmp_baseline: Path) -> None:
    save_baseline({}, tmp_baseline)
    result = diff_from_baseline({"flask": "3.0.0"}, path=tmp_baseline)
    assert result == {"flask": ("", "3.0.0")}


def test_diff_from_baseline_unchanged_excluded(tmp_baseline: Path) -> None:
    save_baseline({"requests": "2.31.0"}, tmp_baseline)
    result = diff_from_baseline({"requests": "2.31.0"}, path=tmp_baseline)
    assert result == {}


def test_diff_from_baseline_accepts_explicit_baseline() -> None:
    baseline = {"requests": "2.28.0", "flask": "2.3.0"}
    current = {"requests": "2.31.0", "flask": "2.3.0"}
    result = diff_from_baseline(current, baseline=baseline)
    assert result == {"requests": ("2.28.0", "2.31.0")}


def test_diff_from_baseline_empty_current_returns_empty(tmp_baseline: Path) -> None:
    save_baseline({"requests": "2.31.0"}, tmp_baseline)
    result = diff_from_baseline({}, path=tmp_baseline)
    assert result == {}
