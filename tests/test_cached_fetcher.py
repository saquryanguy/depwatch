"""Tests for depwatch.cached_fetcher module."""

from pathlib import Path
from unittest.mock import patch

import pytest

import depwatch.cached_fetcher as cf
from depwatch.cache import get_cached, set_cached


@pytest.fixture(autouse=True)
def isolated_cache(tmp_path, monkeypatch):
    """Redirect all cache I/O to a temporary directory for each test."""
    import depwatch.cache as cache_mod
    monkeypatch.setattr(cache_mod, "DEFAULT_CACHE_DIR", tmp_path / "cache")
    # Also patch the constants used inside cached_fetcher via the cache module
    yield tmp_path / "cache"


def test_cached_fetch_pypi_metadata_calls_upstream(isolated_cache):
    fake_meta = {"info": {"name": "requests"}}
    with patch("depwatch.cached_fetcher.fetch_pypi_metadata", return_value=fake_meta) as mock_fn:
        result = cf.cached_fetch_pypi_metadata("requests")
    assert result == fake_meta
    mock_fn.assert_called_once_with("requests")


def test_cached_fetch_pypi_metadata_uses_cache_on_second_call(isolated_cache):
    fake_meta = {"info": {"name": "requests"}}
    with patch("depwatch.cached_fetcher.fetch_pypi_metadata", return_value=fake_meta) as mock_fn:
        cf.cached_fetch_pypi_metadata("requests")
        cf.cached_fetch_pypi_metadata("requests")
    mock_fn.assert_called_once()  # upstream called only once


def test_cached_fetch_pypi_metadata_none_not_cached(isolated_cache):
    with patch("depwatch.cached_fetcher.fetch_pypi_metadata", return_value=None) as mock_fn:
        cf.cached_fetch_pypi_metadata("unknown-pkg")
        cf.cached_fetch_pypi_metadata("unknown-pkg")
    assert mock_fn.call_count == 2  # None result must not be cached


def test_cached_fetch_changelog_from_github_calls_upstream(isolated_cache):
    with patch(
        "depwatch.cached_fetcher.fetch_changelog_from_github", return_value="## 1.0\n- init"
    ) as mock_fn:
        result = cf.cached_fetch_changelog_from_github("psf", "requests")
    assert "1.0" in result
    mock_fn.assert_called_once_with("psf", "requests", "HEAD")


def test_cached_fetch_changelog_from_github_cache_hit(isolated_cache):
    with patch(
        "depwatch.cached_fetcher.fetch_changelog_from_github", return_value="## 2.0"
    ) as mock_fn:
        cf.cached_fetch_changelog_from_github("psf", "requests", ref="main")
        cf.cached_fetch_changelog_from_github("psf", "requests", ref="main")
    mock_fn.assert_called_once()


def test_cached_get_changelog_calls_upstream(isolated_cache):
    with patch("depwatch.cached_fetcher.get_changelog", return_value="changelog text") as mock_fn:
        result = cf.cached_get_changelog("flask")
    assert result == "changelog text"
    mock_fn.assert_called_once_with("flask")


def test_cached_get_changelog_second_call_uses_cache(isolated_cache):
    with patch("depwatch.cached_fetcher.get_changelog", return_value="changelog text") as mock_fn:
        cf.cached_get_changelog("flask")
        cf.cached_get_changelog("flask")
    mock_fn.assert_called_once()
