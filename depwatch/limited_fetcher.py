"""Rate-limited wrappers around cached_fetcher functions."""

from typing import Optional

from depwatch.cached_fetcher import (
    cached_fetch_pypi_metadata,
    cached_fetch_changelog_from_github,
    cached_get_changelog,
)
from depwatch.rate_limiter import pypi_limiter, github_limiter


def limited_fetch_pypi_metadata(package_name: str) -> Optional[dict]:
    """Fetch PyPI metadata with rate limiting applied."""
    if pypi_limiter is not None:
        pypi_limiter.acquire(block=True)
    return cached_fetch_pypi_metadata(package_name)


def limited_fetch_changelog_from_github(
    repo: str, version_from: str, version_to: str
) -> Optional[str]:
    """Fetch changelog from GitHub with rate limiting applied."""
    if github_limiter is not None:
        github_limiter.acquire(block=True)
    return cached_fetch_changelog_from_github(repo, version_from, version_to)


def limited_get_changelog(
    package_name: str, version_from: str, version_to: str
) -> Optional[str]:
    """Get changelog for a package upgrade with rate limiting applied.

    Applies PyPI limiter for metadata lookup and GitHub limiter for
    changelog retrieval.
    """
    if pypi_limiter is not None:
        pypi_limiter.acquire(block=True)
    return cached_get_changelog(package_name, version_from, version_to)
