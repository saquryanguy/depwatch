"""Configuration for changelog trend analysis."""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class TrendConfig:
    enabled: bool = True
    max_history: int = 10  # maximum number of past runs to consider
    min_delta_to_report: float = 0.0  # only report packages with |delta| >= this
    include_improving: bool = True


def config_from_env() -> TrendConfig:
    enabled = os.getenv("DEPWATCH_TREND_ENABLED", "true").lower() != "false"
    try:
        max_history = int(os.getenv("DEPWATCH_TREND_MAX_HISTORY", "10"))
    except ValueError:
        max_history = 10
    try:
        min_delta = float(os.getenv("DEPWATCH_TREND_MIN_DELTA", "0.0"))
    except ValueError:
        min_delta = 0.0
    include_improving = (
        os.getenv("DEPWATCH_TREND_INCLUDE_IMPROVING", "true").lower() != "false"
    )
    return TrendConfig(
        enabled=enabled,
        max_history=max_history,
        min_delta_to_report=min_delta,
        include_improving=include_improving,
    )


def config_from_dict(data: dict) -> TrendConfig:
    enabled = str(data.get("enabled", "true")).lower() != "false"
    try:
        max_history = int(data.get("max_history", 10))
    except (ValueError, TypeError):
        max_history = 10
    try:
        min_delta = float(data.get("min_delta_to_report", 0.0))
    except (ValueError, TypeError):
        min_delta = 0.0
    include_improving = str(data.get("include_improving", "true")).lower() != "false"
    return TrendConfig(
        enabled=enabled,
        max_history=max_history,
        min_delta_to_report=min_delta,
        include_improving=include_improving,
    )
