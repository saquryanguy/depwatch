"""Configuration for the changelog diff renderer."""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Optional

from depwatch.severity_classifier import Severity

_VALID_FORMATS = {"markdown", "plain"}


@dataclass
class DiffRenderConfig:
    output_format: str = "markdown"  # "markdown" | "plain"
    min_severity: Optional[Severity] = None
    include_safe: bool = True
    max_lines_per_package: int = 50


def _parse_severity(value: str) -> Optional[Severity]:
    try:
        return Severity[value.upper()]
    except (KeyError, AttributeError):
        return None


def config_from_env() -> DiffRenderConfig:
    fmt = os.environ.get("DEPWATCH_RENDER_FORMAT", "markdown").lower()
    if fmt not in _VALID_FORMATS:
        fmt = "markdown"

    raw_sev = os.environ.get("DEPWATCH_RENDER_MIN_SEVERITY", "")
    min_sev = _parse_severity(raw_sev) if raw_sev else None

    include_safe_raw = os.environ.get("DEPWATCH_RENDER_INCLUDE_SAFE", "true").lower()
    include_safe = include_safe_raw not in ("false", "0", "no")

    try:
        max_lines = int(os.environ.get("DEPWATCH_RENDER_MAX_LINES", "50"))
    except ValueError:
        max_lines = 50

    return DiffRenderConfig(
        output_format=fmt,
        min_severity=min_sev,
        include_safe=include_safe,
        max_lines_per_package=max_lines,
    )


def config_from_dict(data: dict) -> DiffRenderConfig:
    fmt = str(data.get("output_format", "markdown")).lower()
    if fmt not in _VALID_FORMATS:
        fmt = "markdown"

    raw_sev = data.get("min_severity", "")
    min_sev = _parse_severity(str(raw_sev)) if raw_sev else None

    include_safe = bool(data.get("include_safe", True))

    try:
        max_lines = int(data.get("max_lines_per_package", 50))
    except (TypeError, ValueError):
        max_lines = 50

    return DiffRenderConfig(
        output_format=fmt,
        min_severity=min_sev,
        include_safe=include_safe,
        max_lines_per_package=max_lines,
    )
