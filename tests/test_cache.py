"""Tests for depwatch.cache module."""

import json
import time
from pathlib import Path

import pytest

from depwatch.cache import (
    _cache_key,
    cache_stats,
    clear_cache,
    get_cached,
    set_cached,
)


@pytest.fixture()
def tmp_cache(tmp_path):
    return tmp_path / "cache"


def test_cache_key_is_deterministic():
    assert _cache_key("pypi", "requests") == _cache_key("pypi", "requests")


def test_cache_key_differs_by_namespace():
    assert _cache_key("pypi", "requests") != _cache_key("github", "requests")


def test_cache_key_differs_by_identifier():
    assert _cache_key("pypi", "requests") != _cache_key("pypi", "flask")


def test_set_and_get_cached(tmp_cache):
    set_cached("pypi", "requests", {"version": "2.28"}, cache_dir=tmp_cache)
    result = get_cached("pypi", "requests", cache_dir=tmp_cache)
    assert result == {"version": "2.28"}


def test_get_cached_returns_none_for_missing(tmp_cache):
    result = get_cached("pypi", "nonexistent", cache_dir=tmp_cache)
    assert result is None


def test_get_cached_respects_ttl(tmp_cache):
    set_cached("pypi", "flask", "data", cache_dir=tmp_cache)
    # Manually backdate the timestamp
    key_file = tmp_cache / list(tmp_cache.glob("*.json"))[0].name
    data = json.loads(key_file.read_text())
    data["timestamp"] = time.time() - 7200  # 2 hours ago
    key_file.write_text(json.dumps(data))
    result = get_cached("pypi", "flask", ttl=3600, cache_dir=tmp_cache)
    assert result is None


def test_get_cached_handles_corrupt_file(tmp_cache):
    tmp_cache.mkdir(parents=True, exist_ok=True)
    bad_file = tmp_cache / "pypi_badbadbadbad.json"
    bad_file.write_text("not json")
    # Should not raise, just return None
    result = get_cached("pypi", "corrupt", cache_dir=tmp_cache)
    assert result is None


def test_clear_cache_removes_files(tmp_cache):
    set_cached("ns", "a", 1, cache_dir=tmp_cache)
    set_cached("ns", "b", 2, cache_dir=tmp_cache)
    removed = clear_cache(cache_dir=tmp_cache)
    assert removed == 2
    assert list(tmp_cache.glob("*.json")) == []


def test_clear_cache_nonexistent_dir(tmp_path):
    missing = tmp_path / "no_such_dir"
    assert clear_cache(cache_dir=missing) == 0


def test_cache_stats(tmp_cache):
    set_cached("ns", "x", "hello", cache_dir=tmp_cache)
    stats = cache_stats(cache_dir=tmp_cache)
    assert stats["entries"] == 1
    assert stats["size_bytes"] > 0


def test_cache_stats_empty_dir(tmp_path):
    stats = cache_stats(cache_dir=tmp_path / "empty")
    assert stats == {"entries": 0, "size_bytes": 0}
