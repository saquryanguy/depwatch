"""Configuration for the changelog diff comparator."""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import List, Optional

from depwatch.severity_classifier import Severity


@dataclass
class ComparatorConfig:
    min_severity: Optional[Severity] = None
    only_regressions: bool = False
    ignore_packages: List[str] = field(default_factory=list)


def _parse_severity(value: str) -> Optional[Severity]:
    try:
        return Severity[value.upper()]
    except KeyError:
        return None


def config_from_env() -> ComparatorConfig:
    min_sev_raw = os.environ.get("DEPWATCH_COMPARE_MIN_SEVERITY", "")
    only_reg = os.environ.get("DEPWATCH_COMPARE_ONLY_REGRESSIONS", "false").lower() == "true"
    ignore_raw = os.environ.get("DEPWATCH_COMPARE_IGNORE_PACKAGES", "")
    ignore = [p.strip() for p in ignore_raw.split(",") if p.strip()]
    return ComparatorConfig(
        min_severity=_parse_severity(min_sev_raw) if min_sev_raw else None,
        only_regressions=only_reg,
        ignore_packages=ignore,
    )


def config_from_dict(data: dict) -> ComparatorConfig:
    min_sev_raw = data.get("min_severity", "")
    only_reg_raw = data.get("only_regressions", False)
    ignore_raw = data.get("ignore_packages", [])

    if isinstance(only_reg_raw, str):
        only_reg = only_reg_raw.lower() == "true"
    else:
        only_reg = bool(only_reg_raw)

    if isinstance(ignore_raw, str):
        ignore = [p.strip() for p in ignore_raw.split(",") if p.strip()]
    else:
        ignore = list(ignore_raw)

    return ComparatorConfig(
        min_severity=_parse_severity(min_sev_raw) if min_sev_raw else None,
        only_regressions=only_reg,
        ignore_packages=ignore,
    )
