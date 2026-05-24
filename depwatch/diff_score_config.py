"""Configuration for the changelog diff scorer feature."""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import List, Optional

from depwatch.severity_classifier import Severity


@dataclass
class DiffScoreConfig:
    """Controls how the diff scorer filters and presents results."""

    min_risk_score: int = 0
    """Only include entries whose risk_score >= this value."""

    min_severity: Severity = Severity.SAFE
    """Only include entries at or above this severity."""

    top_n: Optional[int] = None
    """If set, limit output to the top-N riskiest packages."""

    include_safe: bool = True
    """Whether to include packages with zero risk in the report."""

    extra_labels: List[str] = field(default_factory=list)
    """Additional labels to attach to the PR comment."""


def config_from_env() -> DiffScoreConfig:
    """Build a DiffScoreConfig from environment variables."""
    raw_min_risk = os.getenv("DEPWATCH_DIFF_SCORE_MIN_RISK", "0")
    try:
        min_risk = int(raw_min_risk)
    except ValueError:
        min_risk = 0

    raw_severity = os.getenv("DEPWATCH_DIFF_SCORE_MIN_SEVERITY", "safe").lower()
    try:
        min_severity = Severity(raw_severity)
    except ValueError:
        min_severity = Severity.SAFE

    raw_top_n = os.getenv("DEPWATCH_DIFF_SCORE_TOP_N", "")
    try:
        top_n: Optional[int] = int(raw_top_n) if raw_top_n else None
    except ValueError:
        top_n = None

    include_safe_raw = os.getenv("DEPWATCH_DIFF_SCORE_INCLUDE_SAFE", "true").lower()
    include_safe = include_safe_raw not in ("false", "0", "no")

    raw_labels = os.getenv("DEPWATCH_DIFF_SCORE_EXTRA_LABELS", "")
    extra_labels = [lbl.strip() for lbl in raw_labels.split(",") if lbl.strip()]

    return DiffScoreConfig(
        min_risk_score=min_risk,
        min_severity=min_severity,
        top_n=top_n,
        include_safe=include_safe,
        extra_labels=extra_labels,
    )


def config_from_dict(data: dict) -> DiffScoreConfig:
    """Build a DiffScoreConfig from a plain dictionary (e.g. parsed YAML)."""
    raw_severity = str(data.get("min_severity", "safe")).lower()
    try:
        min_severity = Severity(raw_severity)
    except ValueError:
        min_severity = Severity.SAFE

    try:
        min_risk = int(data.get("min_risk_score", 0))
    except (TypeError, ValueError):
        min_risk = 0

    raw_top_n = data.get("top_n")
    try:
        top_n = int(raw_top_n) if raw_top_n is not None else None
    except (TypeError, ValueError):
        top_n = None

    include_safe_raw = str(data.get("include_safe", "true")).lower()
    include_safe = include_safe_raw not in ("false", "0", "no")

    raw_labels = data.get("extra_labels", [])
    if isinstance(raw_labels, str):
        extra_labels = [lbl.strip() for lbl in raw_labels.split(",") if lbl.strip()]
    else:
        extra_labels = [str(lbl) for lbl in raw_labels]

    return DiffScoreConfig(
        min_risk_score=min_risk,
        min_severity=min_severity,
        top_n=top_n,
        include_safe=include_safe,
        extra_labels=extra_labels,
    )
