"""Configuration for the changelog diff summarizer."""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import List, Optional

from depwatch.severity_classifier import Severity


@dataclass
class DiffSummaryConfig:
    min_severity: Optional[Severity] = None
    include_safe: bool = True
    max_headline_length: int = 120
    only_packages: List[str] = field(default_factory=list)


def _parse_severity(value: str) -> Optional[Severity]:
    try:
        return Severity[value.upper()]
    except KeyError:
        return None


def config_from_env() -> DiffSummaryConfig:
    min_sev_raw = os.environ.get("DEPWATCH_SUMMARY_MIN_SEVERITY", "")
    include_safe = os.environ.get("DEPWATCH_SUMMARY_INCLUDE_SAFE", "true").lower() != "false"
    max_len_raw = os.environ.get("DEPWATCH_SUMMARY_MAX_HEADLINE_LENGTH", "120")
    packages_raw = os.environ.get("DEPWATCH_SUMMARY_ONLY_PACKAGES", "")

    try:
        max_len = int(max_len_raw)
    except ValueError:
        max_len = 120

    packages = [p.strip() for p in packages_raw.split(",") if p.strip()] if packages_raw else []

    return DiffSummaryConfig(
        min_severity=_parse_severity(min_sev_raw) if min_sev_raw else None,
        include_safe=include_safe,
        max_headline_length=max_len,
        only_packages=packages,
    )


def config_from_dict(data: dict) -> DiffSummaryConfig:
    min_sev_raw = data.get("min_severity", "")
    include_safe_raw = data.get("include_safe", True)
    max_len_raw = data.get("max_headline_length", 120)
    packages_raw = data.get("only_packages", [])

    if isinstance(include_safe_raw, str):
        include_safe = include_safe_raw.lower() != "false"
    else:
        include_safe = bool(include_safe_raw)

    try:
        max_len = int(max_len_raw)
    except (ValueError, TypeError):
        max_len = 120

    if isinstance(packages_raw, str):
        packages = [p.strip() for p in packages_raw.split(",") if p.strip()]
    else:
        packages = list(packages_raw)

    return DiffSummaryConfig(
        min_severity=_parse_severity(min_sev_raw) if min_sev_raw else None,
        include_safe=include_safe,
        max_headline_length=max_len,
        only_packages=packages,
    )
