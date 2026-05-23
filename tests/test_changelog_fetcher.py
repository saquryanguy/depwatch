"""Tests for changelog_fetcher module."""

import pytest
import httpx
from unittest.mock import patch, MagicMock

from depwatch.changelog_fetcher import (
    extract_github_repo,
    fetch_changelog_from_github,
    get_changelog,
)


SAMPLE_METADATA = {
    "info": {
        "project_urls": {
            "Source": "https://github.com/psf/requests",
        }
    }
}


def test_extract_github_repo_from_source():
    repo = extract_github_repo(SAMPLE_METADATA)
    assert repo == "psf/requests"


def test_extract_github_repo_missing():
    repo = extract_github_repo({"info": {"project_urls": {}}})
    assert repo is None


def test_extract_github_repo_no_project_urls():
    repo = extract_github_repo({"info": {}})
    assert repo is None


@patch("depwatch.changelog_fetcher.httpx.get")
def test_fetch_changelog_from_github_success(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = "## 1.0.0\n- Initial release"
    mock_get.return_value = mock_response

    result = fetch_changelog_from_github("psf/requests")
    assert result == "## 1.0.0\n- Initial release"


@patch("depwatch.changelog_fetcher.httpx.get")
def test_fetch_changelog_from_github_not_found(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_get.return_value = mock_response

    result = fetch_changelog_from_github("psf/requests", branch="master")
    assert result is None


@patch("depwatch.changelog_fetcher.fetch_changelog_from_github")
@patch("depwatch.changelog_fetcher.fetch_pypi_metadata")
def test_get_changelog_success(mock_meta, mock_fetch):
    mock_meta.return_value = SAMPLE_METADATA
    mock_fetch.return_value = "## 2.0.0\n- Breaking change"

    result = get_changelog("requests")
    assert "Breaking change" in result


@patch("depwatch.changelog_fetcher.fetch_pypi_metadata", side_effect=httpx.HTTPError("err"))
def test_get_changelog_http_error(mock_meta):
    result = get_changelog("nonexistent-pkg")
    assert result is None
