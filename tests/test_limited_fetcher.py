"""Tests for depwatch.limited_fetcher."""

from unittest.mock import patch, MagicMock

import pytest

import depwatch.rate_limiter as rate_limiter_module
from depwatch.limited_fetcher import (
    limited_fetch_pypi_metadata,
    limited_fetch_changelog_from_github,
    limited_get_changelog,
)


@pytest.fixture(autouse=True)
def fast_limiters():
    """Replace module-level limiters with high-capacity ones to keep tests fast."""
    from depwatch.rate_limiter import RateLimiter
    original_pypi = rate_limiter_module.pypi_limiter
    original_github = rate_limiter_module.github_limiter
    rate_limiter_module.pypi_limiter = RateLimiter(max_calls=100, window_seconds=1.0)
    rate_limiter_module.github_limiter = RateLimiter(max_calls=100, window_seconds=1.0)
    yield
    rate_limiter_module.pypi_limiter = original_pypi
    rate_limiter_module.github_limiter = original_github


def test_limited_fetch_pypi_metadata_calls_upstream():
    with patch("depwatch.limited_fetcher.cached_fetch_pypi_metadata") as mock:
        mock.return_value = {"info": {"name": "requests"}}
        result = limited_fetch_pypi_metadata("requests")
        mock.assert_called_once_with("requests")
        assert result == {"info": {"name": "requests"}}


def test_limited_fetch_pypi_metadata_respects_limiter():
    """Limiter.acquire() should be called before the upstream fetch."""
    mock_limiter = MagicMock()
    mock_limiter.acquire.return_value = True
    rate_limiter_module.pypi_limiter = mock_limiter

    with patch("depwatch.limited_fetcher.cached_fetch_pypi_metadata", return_value=None):
        limited_fetch_pypi_metadata("boto3")
        mock_limiter.acquire.assert_called_once_with(block=True)


def test_limited_fetch_changelog_from_github_calls_upstream():
    with patch("depwatch.limited_fetcher.cached_fetch_changelog_from_github") as mock:
        mock.return_value = "## 2.0.0\n- breaking change"
        result = limited_fetch_changelog_from_github("owner/repo", "1.0.0", "2.0.0")
        mock.assert_called_once_with("owner/repo", "1.0.0", "2.0.0")
        assert "breaking" in result


def test_limited_fetch_changelog_from_github_respects_limiter():
    mock_limiter = MagicMock()
    mock_limiter.acquire.return_value = True
    rate_limiter_module.github_limiter = mock_limiter

    with patch("depwatch.limited_fetcher.cached_fetch_changelog_from_github", return_value=None):
        limited_fetch_changelog_from_github("owner/repo", "1.0", "2.0")
        mock_limiter.acquire.assert_called_once_with(block=True)


def test_limited_get_changelog_calls_upstream():
    with patch("depwatch.limited_fetcher.cached_get_changelog") as mock:
        mock.return_value = "changelog text"
        result = limited_get_changelog("flask", "2.0.0", "3.0.0")
        mock.assert_called_once_with("flask", "2.0.0", "3.0.0")
        assert result == "changelog text"


def test_limited_get_changelog_none_result_propagated():
    with patch("depwatch.limited_fetcher.cached_get_changelog", return_value=None):
        result = limited_get_changelog("flask", "2.0.0", "3.0.0")
        assert result is None


def test_limited_get_changelog_respects_limiter():
    """Limiter.acquire() should be called before the upstream changelog fetch."""
    mock_limiter = MagicMock()
    mock_limiter.acquire.return_value = True
    rate_limiter_module.pypi_limiter = mock_limiter

    with patch("depwatch.limited_fetcher.cached_get_changelog", return_value=None):
        limited_get_changelog("django", "3.0.0", "4.0.0")
        mock_limiter.acquire.assert_called_once_with(block=True)
