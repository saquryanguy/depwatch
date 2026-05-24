"""Apply GitHub PR labels based on changelog analysis results."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import List, Optional

import requests

from depwatch.label_mapper import LabelSet


@dataclass
class LabelingResult:
    pr_number: int
    repo: str
    applied: List[str] = field(default_factory=list)
    skipped: List[str] = field(default_factory=list)
    error: Optional[str] = None

    @property
    def success(self) -> bool:
        return self.error is None


def _github_token() -> Optional[str]:
    return os.environ.get("GITHUB_TOKEN")


def _labels_api_url(repo: str, pr_number: int) -> str:
    return f"https://api.github.com/repos/{repo}/issues/{pr_number}/labels"


def fetch_existing_labels(repo: str, pr_number: int, token: str) -> List[str]:
    """Return the names of labels already on the PR."""
    url = _labels_api_url(repo, pr_number)
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
    }
    resp = requests.get(url, headers=headers, timeout=10)
    if resp.status_code != 200:
        return []
    return [lbl["name"] for lbl in resp.json()]


def apply_labels(
    repo: str,
    pr_number: int,
    label_set: LabelSet,
    token: Optional[str] = None,
) -> LabelingResult:
    """Apply labels derived from *label_set* to a GitHub PR.

    Labels that are already present on the PR are skipped.
    """
    token = token or _github_token()
    result = LabelingResult(pr_number=pr_number, repo=repo)

    if not token:
        result.error = "GITHUB_TOKEN not set"
        return result

    desired = label_set.all_labels()
    if not desired:
        return result

    existing = fetch_existing_labels(repo, pr_number, token)
    to_apply = [lbl for lbl in desired if lbl not in existing]
    already_there = [lbl for lbl in desired if lbl in existing]
    result.skipped.extend(already_there)

    if not to_apply:
        return result

    url = _labels_api_url(repo, pr_number)
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
    }
    resp = requests.post(url, json={"labels": to_apply}, headers=headers, timeout=10)
    if resp.status_code in (200, 201):
        result.applied.extend(to_apply)
    else:
        result.error = f"GitHub API error {resp.status_code}: {resp.text[:200]}"

    return result
