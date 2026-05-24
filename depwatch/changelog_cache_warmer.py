"""Pre-warms the changelog cache for a list of packages.

Useful for batch-fetching changelogs before the main pipeline runs,
reducing latency and rate-limit pressure during analysis.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable

from depwatch.cached_fetcher import cached_get_changelog


@dataclass
class WarmResult:
    """Outcome of a cache warm operation for a single package."""

    package: str
    version: str
    success: bool
    cached: bool = False  # True if already present before warming
    error: str | None = None


@dataclass
class WarmSummary:
    """Aggregate outcome of warming multiple packages."""

    results: list[WarmResult] = field(default_factory=list)

    @property
    def total(self) -> int:
        return len(self.results)

    @property
    def succeeded(self) -> int:
        return sum(1 for r in self.results if r.success)

    @property
    def failed(self) -> int:
        return sum(1 for r in self.results if not r.success)

    @property
    def already_cached(self) -> int:
        return sum(1 for r in self.results if r.cached)


def warm_package(package: str, version: str) -> WarmResult:
    """Fetch and cache changelog for a single package/version pair."""
    try:
        result = cached_get_changelog(package, version)
        return WarmResult(
            package=package,
            version=version,
            success=True,
            cached=result is None,  # None means no changelog found but call succeeded
        )
    except Exception as exc:  # noqa: BLE001
        return WarmResult(
            package=package,
            version=version,
            success=False,
            error=str(exc),
        )


def warm_cache(
    packages: Iterable[tuple[str, str]],
) -> WarmSummary:
    """Warm the changelog cache for an iterable of (package, version) pairs.

    Args:
        packages: Iterable of (package_name, version) tuples.

    Returns:
        WarmSummary with per-package results.
    """
    summary = WarmSummary()
    for package, version in packages:
        result = warm_package(package, version)
        summary.results.append(result)
    return summary
