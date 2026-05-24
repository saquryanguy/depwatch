"""Parse ExportConfig from environment variables or a plain dict."""
from __future__ import annotations

import os
from depwatch.changelog_exporter import ExportConfig

_VALID_FORMATS = {"markdown", "plain", "json"}


def config_from_env() -> ExportConfig:
    """Build an ExportConfig from DEPWATCH_EXPORT_* environment variables."""
    fmt = os.getenv("DEPWATCH_EXPORT_FORMAT", "markdown").lower()
    if fmt not in _VALID_FORMATS:
        fmt = "markdown"

    output_path = os.getenv("DEPWATCH_EXPORT_PATH") or None
    include_safe_raw = os.getenv("DEPWATCH_EXPORT_INCLUDE_SAFE", "false").lower()
    include_safe = include_safe_raw in {"1", "true", "yes"}

    return ExportConfig(
        output_format=fmt,
        output_path=output_path,
        include_safe=include_safe,
    )


def config_from_dict(data: dict) -> ExportConfig:
    """Build an ExportConfig from a plain dictionary (e.g. parsed YAML)."""
    fmt = str(data.get("output_format", "markdown")).lower()
    if fmt not in _VALID_FORMATS:
        fmt = "markdown"

    output_path = data.get("output_path") or None
    include_safe = bool(data.get("include_safe", False))

    return ExportConfig(
        output_format=fmt,
        output_path=output_path,
        include_safe=include_safe,
    )
