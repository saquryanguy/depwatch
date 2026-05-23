"""Tests for depwatch.retried_fetcher."""

import pytest
from unittest.mock import patch, MagicMock

from depwatch.retried_fetcher import (
    retried_fetch_pypi_metadata,
    retried_fetch_changelog_from_github,
    retried_get_changelog,
)


# ---------------------------------------------------------------------------
# retried_fetch_pypi_metadata
# ---------------------------------------------------------------------------

def test_retried_fetch_pypi_metadata_returns_result():
    with patch("depwatch.retried_fetcher.fetch_pypi_metadata", return_value={"info": {}}) as mock:
        result = retried_fetch_pypi_metadata("requests")
    assert result == {"info": {}}
    mock.assert_called_once_with("requests")


def test_retried_fetch_pypi_metadata_retries_on_os_error():
    sleeps = []
    call_count = 0

    def flaky():
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise OSError("network down")
        return {"info": {"name": "requests"}}

    with patch("depwatch.retried_fetcher.fetch_pypi_metadata", side_effect=lambda _: flaky()):
        result = retried_fetch_pypi_metadata("requests", retries=3, backoff_base=0.0)

    assert result == {"info": {"name": "requests"}}
    assert call_count == 3


def test_retried_fetch_pypi_metadata_raises_after_exhaustion():
    with patch("depwatch.retried_fetcher.fetch_pypi_metadata", side_effect=OSError("timeout")):
        with pytest.raises(OSError, match="timeout"):
            retried_fetch_pypi_metadata("requests", retries=2, backoff_base=0.0)


# ---------------------------------------------------------------------------
# retried_fetch_changelog_from_github
# ---------------------------------------------------------------------------

def test_retried_fetch_changelog_from_github_returns_result():
    with patch("depwatch.retried_fetcher.fetch_changelog_from_github", return_value="## 1.0.0") as mock:
        result = retried_fetch_changelog_from_github("owner/repo")
    assert result == "## 1.0.0"
    mock.assert_called_once_with("owner/repo")


def test_retried_fetch_changelog_from_github_retries_on_connection_error():
    attempts = []

    def flaky(repo):
        attempts.append(repo)
        if len(attempts) < 2:
            raise ConnectionError("refused")
        return "## 2.0.0"

    with patch("depwatch.retried_fetcher.fetch_changelog_from_github", side_effect=flaky):
        result = retried_fetch_changelog_from_github("owner/repo", retries=3, backoff_base=0.0)

    assert result == "## 2.0.0"
    assert len(attempts) == 2


# ---------------------------------------------------------------------------
# retried_get_changelog
# ---------------------------------------------------------------------------

def test_retried_get_changelog_returns_result():
    with patch("depwatch.retried_fetcher.get_changelog", return_value="## Changelog") as mock:
        result = retried_get_changelog("mypackage")
    assert result == "## Changelog"
    mock.assert_called_once_with("mypackage")


def test_retried_get_changelog_returns_none_without_retry():
    with patch("depwatch.retried_fetcher.get_changelog", return_value=None):
        result = retried_get_changelog("unknown-pkg")
    assert result is None
