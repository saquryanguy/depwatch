"""Tests for depwatch.changelog_cache_warmer."""

from __future__ import annotations

from unittest.mock import patch

import pytest

from depwatch.changelog_cache_warmer import (
    WarmResult,
    WarmSummary,
    warm_cache,
    warm_package,
)

MODULE = "depwatch.changelog_cache_warmer"


# ---------------------------------------------------------------------------
# WarmResult / WarmSummary dataclass tests
# ---------------------------------------------------------------------------


def test_warm_result_defaults():
    r = WarmResult(package="requests", version="2.31.0", success=True)
    assert r.cached is False
    assert r.error is None


def test_warm_summary_counts_empty():
    s = WarmSummary()
    assert s.total == 0
    assert s.succeeded == 0
    assert s.failed == 0
    assert s.already_cached == 0


def test_warm_summary_counts_mixed():
    results = [
        WarmResult("a", "1.0", success=True, cached=False),
        WarmResult("b", "2.0", success=True, cached=True),
        WarmResult("c", "3.0", success=False, error="timeout"),
    ]
    s = WarmSummary(results=results)
    assert s.total == 3
    assert s.succeeded == 2
    assert s.failed == 1
    assert s.already_cached == 1


# ---------------------------------------------------------------------------
# warm_package tests
# ---------------------------------------------------------------------------


def test_warm_package_success():
    with patch(f"{MODULE}.cached_get_changelog", return_value="## 1.0\n- added stuff") as mock:
        result = warm_package("requests", "2.31.0")

    mock.assert_called_once_with("requests", "2.31.0")
    assert result.success is True
    assert result.package == "requests"
    assert result.version == "2.31.0"
    assert result.error is None


def test_warm_package_none_changelog_still_success():
    with patch(f"{MODULE}.cached_get_changelog", return_value=None):
        result = warm_package("unknown-pkg", "0.1.0")

    assert result.success is True
    assert result.cached is True  # None triggers cached=True branch


def test_warm_package_exception_returns_failure():
    with patch(f"{MODULE}.cached_get_changelog", side_effect=OSError("network error")):
        result = warm_package("bad-pkg", "1.0.0")

    assert result.success is False
    assert "network error" in (result.error or "")


# ---------------------------------------------------------------------------
# warm_cache tests
# ---------------------------------------------------------------------------


def test_warm_cache_returns_summary():
    packages = [("requests", "2.31.0"), ("flask", "3.0.0")]
    with patch(f"{MODULE}.cached_get_changelog", return_value="## changelog"):
        summary = warm_cache(packages)

    assert isinstance(summary, WarmSummary)
    assert summary.total == 2
    assert summary.succeeded == 2
    assert summary.failed == 0


def test_warm_cache_partial_failure():
    def _side_effect(pkg, ver):
        if pkg == "bad":
            raise RuntimeError("boom")
        return "## ok"

    packages = [("good", "1.0"), ("bad", "2.0")]
    with patch(f"{MODULE}.cached_get_changelog", side_effect=_side_effect):
        summary = warm_cache(packages)

    assert summary.succeeded == 1
    assert summary.failed == 1


def test_warm_cache_empty_input():
    summary = warm_cache([])
    assert summary.total == 0
