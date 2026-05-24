"""Configuration for changelog diff grouping behaviour."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional

from depwatch.severity_classifier import Severity


@dataclass
class DiffGroupConfig:
    min_severity: Optional[Severity] = None
    include_safe: bool = True
    max_packages_per_group: int = 50


def _parse_severity(value: str) -> Optional[Severity]:
    try:
        return Severity[value.upper()]
    except (KeyError, AttributeError):
        return None


def config_from_env() -> DiffGroupConfig:
    min_sev = _parse_severity(os.getenv("DEPWATCH_GROUP_MIN_SEVERITY", ""))
    include_safe_raw = os.getenv("DEPWATCH_GROUP_INCLUDE_SAFE", "true").lower()
    include_safe = include_safe_raw not in ("false", "0", "no")
    try:
        max_pkg = int(os.getenv("DEPWATCH_GROUP_MAX_PACKAGES", "50"))
    except ValueError:
        max_pkg = 50
    return DiffGroupConfig(
        min_severity=min_sev,
        include_safe=include_safe,
        max_packages_per_group=max_pkg,
    )


def config_from_dict(data: dict) -> DiffGroupConfig:
    min_sev = _parse_severity(data.get("min_severity", "") or "")
    include_safe_raw = str(data.get("include_safe", True)).lower()
    include_safe = include_safe_raw not in ("false", "0", "no")
    try:
        max_pkg = int(data.get("max_packages_per_group", 50))
    except (ValueError, TypeError):
        max_pkg = 50
    return DiffGroupConfig(
        min_severity=min_sev,
        include_safe=include_safe,
        max_packages_per_group=max_pkg,
    )
