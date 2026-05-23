"""Caching wrapper around changelog_fetcher functions."""

from typing import Optional

from depwatch.cache import get_cached, set_cached
from depwatch.changelog_fetcher import (
    fetch_changelog_from_github,
    fetch_pypi_metadata,
    get_changelog,
)

_PYPI_NS = "pypi_meta"
_CHANGELOG_NS = "changelog"
_TTL = 3600


def cached_fetch_pypi_metadata(package: str) -> Optional[dict]:
    """Return PyPI metadata for *package*, using cache when available."""
    cached = get_cached(_PYPI_NS, package, ttl=_TTL)
    if cached is not None:
        return cached
    result = fetch_pypi_metadata(package)
    if result is not None:
        set_cached(_PYPI_NS, package, result)
    return result


def cached_fetch_changelog_from_github(
    owner: str, repo: str, ref: str = "HEAD"
) -> Optional[str]:
    """Return raw changelog text from GitHub, using cache when available."""
    identifier = f"{owner}/{repo}@{ref}"
    cached = get_cached(_CHANGELOG_NS, identifier, ttl=_TTL)
    if cached is not None:
        return cached
    result = fetch_changelog_from_github(owner, repo, ref)
    if result is not None:
        set_cached(_CHANGELOG_NS, identifier, result)
    return result


def cached_get_changelog(package: str) -> Optional[str]:
    """Return full changelog for *package*, using cache when available.

    Falls back to the uncached implementation on cache miss.
    """
    cached = get_cached(_CHANGELOG_NS, package, ttl=_TTL)
    if cached is not None:
        return cached
    result = get_changelog(package)
    if result is not None:
        set_cached(_CHANGELOG_NS, package, result)
    return result
