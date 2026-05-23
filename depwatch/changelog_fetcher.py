"""Fetches changelog content for a given package from common sources."""

import httpx
from typing import Optional

PYPI_URL = "https://pypi.org/pypi/{package}/json"
GITHUB_RAW_URL = "https://raw.githubusercontent.com/{repo}/{branch}/{filename}"
CHANGELOG_FILENAMES = ["CHANGELOG.md", "CHANGELOG.rst", "CHANGES.md", "HISTORY.md"]


def fetch_pypi_metadata(package: str) -> dict:
    """Fetch package metadata from PyPI."""
    url = PYPI_URL.format(package=package)
    response = httpx.get(url, timeout=10)
    response.raise_for_status()
    return response.json()


def extract_github_repo(metadata: dict) -> Optional[str]:
    """Extract GitHub repo path (owner/repo) from PyPI metadata."""
    urls = metadata.get("info", {}).get("project_urls") or {}
    for key in ("Source", "Homepage", "Repository", "Source Code"):
        url = urls.get(key, "")
        if "github.com" in url:
            parts = url.rstrip("/").split("github.com/")
            if len(parts) == 2:
                return "/".join(parts[1].split("/")[:2])
    return None


def fetch_changelog_from_github(repo: str, branch: str = "main") -> Optional[str]:
    """Try to fetch a changelog file from a GitHub repository."""
    for filename in CHANGELOG_FILENAMES:
        url = GITHUB_RAW_URL.format(repo=repo, branch=branch, filename=filename)
        try:
            response = httpx.get(url, timeout=10)
            if response.status_code == 200:
                return response.text
        except httpx.RequestError:
            continue
    # Retry with 'master' branch if 'main' fails
    if branch == "main":
        return fetch_changelog_from_github(repo, branch="master")
    return None


def get_changelog(package: str) -> Optional[str]:
    """High-level function to retrieve changelog text for a package."""
    try:
        metadata = fetch_pypi_metadata(package)
    except httpx.HTTPError:
        return None

    repo = extract_github_repo(metadata)
    if not repo:
        return None

    return fetch_changelog_from_github(repo)
