"""Tests for depwatch.pr_comment."""

import pytest
from unittest.mock import patch, MagicMock
from depwatch.pr_comment import build_comment_body, post_pr_comment, get_github_token


def test_build_comment_body_contains_package():
    body = build_comment_body("requests", "2.28.0", "2.31.0", "No breaking changes detected.")
    assert "requests" in body


def test_build_comment_body_contains_versions():
    body = build_comment_body("requests", "2.28.0", "2.31.0", "No breaking changes detected.")
    assert "2.28.0" in body
    assert "2.31.0" in body


def test_build_comment_body_contains_summary():
    summary = "### ⚠️ Breaking Changes Detected"
    body = build_comment_body("flask", "2.0.0", "3.0.0", summary)
    assert summary in body


def test_build_comment_body_contains_footer():
    body = build_comment_body("flask", "2.0.0", "3.0.0", "summary")
    assert "depwatch" in body


def test_get_github_token_missing(monkeypatch):
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    with pytest.raises(EnvironmentError, match="GITHUB_TOKEN"):
        get_github_token()


def test_get_github_token_present(monkeypatch):
    monkeypatch.setenv("GITHUB_TOKEN", "test-token-123")
    assert get_github_token() == "test-token-123"


@patch("depwatch.pr_comment.requests.post")
def test_post_pr_comment_success(mock_post, monkeypatch):
    monkeypatch.setenv("GITHUB_TOKEN", "fake-token")
    mock_response = MagicMock()
    mock_response.json.return_value = {"id": 42, "body": "comment"}
    mock_post.return_value = mock_response

    result = post_pr_comment("owner/repo", 7, "Hello PR")

    mock_post.assert_called_once()
    assert result["id"] == 42


@patch("depwatch.pr_comment.requests.post")
def test_post_pr_comment_raises_on_http_error(mock_post, monkeypatch):
    monkeypatch.setenv("GITHUB_TOKEN", "fake-token")
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = Exception("403 Forbidden")
    mock_post.return_value = mock_response

    with pytest.raises(Exception, match="403"):
        post_pr_comment("owner/repo", 1, "body")
