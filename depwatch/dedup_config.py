"""Configuration for the changelog diff deduplicator."""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class DedupConfig:
    """Controls deduplication behaviour."""
    enabled: bool = True
    min_removed: int = 0
    report_stats: bool = False


def config_from_env() -> DedupConfig:
    """Build a DedupConfig from environment variables."""
    enabled_raw = os.environ.get("DEPWATCH_DEDUP_ENABLED", "true").lower()
    enabled = enabled_raw not in ("false", "0", "no")

    try:
        min_removed = int(os.environ.get("DEPWATCH_DEDUP_MIN_REMOVED", "0"))
    except ValueError:
        min_removed = 0

    report_stats_raw = os.environ.get("DEPWATCH_DEDUP_REPORT_STATS", "false").lower()
    report_stats = report_stats_raw in ("true", "1", "yes")

    return DedupConfig(
        enabled=enabled,
        min_removed=min_removed,
        report_stats=report_stats,
    )


def config_from_dict(data: Dict[str, Any]) -> DedupConfig:
    """Build a DedupConfig from a plain dictionary."""
    enabled_raw = str(data.get("enabled", "true")).lower()
    enabled = enabled_raw not in ("false", "0", "no")

    try:
        min_removed = int(data.get("min_removed", 0))
    except (ValueError, TypeError):
        min_removed = 0

    report_stats_raw = str(data.get("report_stats", "false")).lower()
    report_stats = report_stats_raw in ("true", "1", "yes")

    return DedupConfig(
        enabled=enabled,
        min_removed=min_removed,
        report_stats=report_stats,
    )
