"""Tests for depwatch.pr_labeler."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from depwatch.label_mapper import LabelSet
from depwatch.pr_labeler import (
    LabelingResult,
    apply_labels,
    fetch_existing_labels,
)


REPO = "owner/repo"
PR = 42
TOKEN = "ghp_test"


def _label_set(*labels: str) -> LabelSet:
    return LabelSet(labels=list(labels))


# ---------------------------------------------------------------------------
# LabelingResult
# ---------------------------------------------------------------------------

def test_labeling_result_success_when_no_error():
    r = LabelingResult(pr_number=1, repo=REPO)
    assert r.success is True


def test_labeling_result_failure_when_error():
    r = LabelingResult(pr_number=1, repo=REPO, error="boom")
    assert r.success is False


# ---------------------------------------------------------------------------
# fetch_existing_labels
# ---------------------------------------------------------------------------

def test_fetch_existing_labels_returns_names():
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = [{"name": "breaking"}, {"name": "critical"}]
    with patch("depwatch.pr_labeler.requests.get", return_value=mock_resp):
        labels = fetch_existing_labels(REPO, PR, TOKEN)
    assert labels == ["breaking", "critical"]


def test_fetch_existing_labels_non_200_returns_empty():
    mock_resp = MagicMock()
    mock_resp.status_code = 404
    with patch("depwatch.pr_labeler.requests.get", return_value=mock_resp):
        labels = fetch_existing_labels(REPO, PR, TOKEN)
    assert labels == []


# ---------------------------------------------------------------------------
# apply_labels
# ---------------------------------------------------------------------------

def test_apply_labels_no_token_returns_error():
    ls = _label_set("breaking")
    with patch("depwatch.pr_labeler._github_token", return_value=None):
        result = apply_labels(REPO, PR, ls, token=None)
    assert result.error is not None
    assert "GITHUB_TOKEN" in result.error


def test_apply_labels_empty_label_set_returns_success():
    ls = _label_set()
    result = apply_labels(REPO, PR, ls, token=TOKEN)
    assert result.success
    assert result.applied == []


def test_apply_labels_posts_new_labels():
    ls = _label_set("breaking", "critical")
    get_resp = MagicMock(status_code=200)
    get_resp.json.return_value = []  # no existing labels
    post_resp = MagicMock(status_code=200)
    with patch("depwatch.pr_labeler.requests.get", return_value=get_resp), \
         patch("depwatch.pr_labeler.requests.post", return_value=post_resp) as mock_post:
        result = apply_labels(REPO, PR, ls, token=TOKEN)
    assert result.success
    assert set(result.applied) == {"breaking", "critical"}
    assert result.skipped == []
    mock_post.assert_called_once()


def test_apply_labels_skips_existing():
    ls = _label_set("breaking", "critical")
    get_resp = MagicMock(status_code=200)
    get_resp.json.return_value = [{"name": "breaking"}]
    post_resp = MagicMock(status_code=200)
    with patch("depwatch.pr_labeler.requests.get", return_value=get_resp), \
         patch("depwatch.pr_labeler.requests.post", return_value=post_resp):
        result = apply_labels(REPO, PR, ls, token=TOKEN)
    assert "critical" in result.applied
    assert "breaking" in result.skipped


def test_apply_labels_api_error_sets_error():
    ls = _label_set("breaking")
    get_resp = MagicMock(status_code=200)
    get_resp.json.return_value = []
    post_resp = MagicMock(status_code=422, text="Unprocessable")
    with patch("depwatch.pr_labeler.requests.get", return_value=get_resp), \
         patch("depwatch.pr_labeler.requests.post", return_value=post_resp):
        result = apply_labels(REPO, PR, ls, token=TOKEN)
    assert not result.success
    assert "422" in result.error
