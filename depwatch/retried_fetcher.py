"""Wrappers around changelog_fetcher that add automatic retry with backoff."""

from typing import Optional, Dict, Any

from depwatch.changelog_fetcher import (
    fetch_pypi_metadata,
    fetch_changelog_from_github,
    get_changelog,
)
from depwatch.retry import with_retry, DEFAULT_RETRIES, DEFAULT_BACKOFF_BASE

_NETWORK_ERRORS: tuple = (OSError, ConnectionError, TimeoutError)

try:
    import requests
    _NETWORK_ERRORS = (OSError, ConnectionError, TimeoutError, requests.RequestException)  # type: ignore[assignment]
except ImportError:
    pass


def retried_fetch_pypi_metadata(
    package: str,
    retries: int = DEFAULT_RETRIES,
    backoff_base: float = DEFAULT_BACKOFF_BASE,
) -> Optional[Dict[str, Any]]:
    """Fetch PyPI metadata for *package* with retry on transient errors."""
    return with_retry(
        lambda: fetch_pypi_metadata(package),
        retries=retries,
        backoff_base=backoff_base,
        retriable_exceptions=tuple(_NETWORK_ERRORS),
    )


def retried_fetch_changelog_from_github(
    repo: str,
    retries: int = DEFAULT_RETRIES,
    backoff_base: float = DEFAULT_BACKOFF_BASE,
) -> Optional[str]:
    """Fetch a changelog file from *repo* on GitHub with retry."""
    return with_retry(
        lambda: fetch_changelog_from_github(repo),
        retries=retries,
        backoff_base=backoff_base,
        retriable_exceptions=tuple(_NETWORK_ERRORS),
    )


def retried_get_changelog(
    package: str,
    retries: int = DEFAULT_RETRIES,
    backoff_base: float = DEFAULT_BACKOFF_BASE,
) -> Optional[str]:
    """Resolve and fetch the changelog for *package* with retry."""
    return with_retry(
        lambda: get_changelog(package),
        retries=retries,
        backoff_base=backoff_base,
        retriable_exceptions=tuple(_NETWORK_ERRORS),
    )
