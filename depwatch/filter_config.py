"""Parse FilterCriteria from environment variables or a config dict."""

from __future__ import annotations

import os
from typing import Any, Dict, List

from depwatch.filter_engine import FilterCriteria
from depwatch.severity_classifier import Severity

_SEVERITY_MAP: Dict[str, Severity] = {
    "low": Severity.LOW,
    "medium": Severity.MEDIUM,
    "high": Severity.HIGH,
    "critical": Severity.CRITICAL,
}

# Environment variable names
_ENV_MIN_SEVERITY = "DEPWATCH_MIN_SEVERITY"
_ENV_PACKAGES = "DEPWATCH_PACKAGES"   # comma-separated
_ENV_KEYWORDS = "DEPWATCH_KEYWORDS"   # comma-separated


def _parse_csv(value: str) -> List[str]:
    """Split a comma-separated string into a stripped, non-empty list."""
    return [item.strip() for item in value.split(",") if item.strip()]


def criteria_from_env() -> FilterCriteria:
    """Build :class:`FilterCriteria` from environment variables.

    Recognised variables:
    - ``DEPWATCH_MIN_SEVERITY``: one of low / medium / high / critical (default: low)
    - ``DEPWATCH_PACKAGES``: comma-separated package names (default: all)
    - ``DEPWATCH_KEYWORDS``: comma-separated keywords (default: none)
    """
    raw_severity = os.environ.get(_ENV_MIN_SEVERITY, "low").lower()
    min_severity = _SEVERITY_MAP.get(raw_severity, Severity.LOW)

    raw_packages = os.environ.get(_ENV_PACKAGES, "")
    packages = _parse_csv(raw_packages) if raw_packages else []

    raw_keywords = os.environ.get(_ENV_KEYWORDS, "")
    keywords = _parse_csv(raw_keywords) if raw_keywords else []

    return FilterCriteria(
        min_severity=min_severity,
        packages=packages,
        keywords=keywords,
    )


def criteria_from_dict(config: Dict[str, Any]) -> FilterCriteria:
    """Build :class:`FilterCriteria` from a plain dictionary (e.g. parsed YAML/JSON).

    Accepted keys: ``min_severity``, ``packages``, ``keywords``.
    """
    raw_severity = str(config.get("min_severity", "low")).lower()
    min_severity = _SEVERITY_MAP.get(raw_severity, Severity.LOW)

    packages: List[str] = list(config.get("packages") or [])
    keywords: List[str] = list(config.get("keywords") or [])

    return FilterCriteria(
        min_severity=min_severity,
        packages=packages,
        keywords=keywords,
    )
