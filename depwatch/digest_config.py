"""Configuration helpers for digest output options."""

import os
from dataclasses import dataclass
from typing import Optional

from depwatch.severity_classifier import Severity

_SEVERITY_MAP = {
    "safe": Severity.SAFE,
    "low": Severity.LOW,
    "medium": Severity.MEDIUM,
    "high": Severity.HIGH,
    "critical": Severity.CRITICAL,
}


@dataclass
class DigestConfig:
    min_severity: Severity = Severity.LOW
    include_safe: bool = False
    output_format: str = "markdown"  # "markdown" or "plain"
    max_packages_shown: Optional[int] = None


def config_from_env() -> DigestConfig:
    """Read DigestConfig from environment variables."""
    raw_severity = os.environ.get("DEPWATCH_DIGEST_MIN_SEVERITY", "low").lower()
    min_severity = _SEVERITY_MAP.get(raw_severity, Severity.LOW)

    include_safe_raw = os.environ.get("DEPWATCH_DIGEST_INCLUDE_SAFE", "false").lower()
    include_safe = include_safe_raw in ("1", "true", "yes")

    output_format = os.environ.get("DEPWATCH_DIGEST_FORMAT", "markdown").lower()
    if output_format not in ("markdown", "plain"):
        output_format = "markdown"

    max_raw = os.environ.get("DEPWATCH_DIGEST_MAX_PACKAGES", "")
    max_packages: Optional[int] = None
    if max_raw.isdigit():
        max_packages = int(max_raw)

    return DigestConfig(
        min_severity=min_severity,
        include_safe=include_safe,
        output_format=output_format,
        max_packages_shown=max_packages,
    )


def config_from_dict(data: dict) -> DigestConfig:
    """Build DigestConfig from a plain dictionary (e.g. parsed YAML)."""
    raw_severity = str(data.get("min_severity", "low")).lower()
    min_severity = _SEVERITY_MAP.get(raw_severity, Severity.LOW)

    include_safe = bool(data.get("include_safe", False))
    output_format = str(data.get("output_format", "markdown")).lower()
    if output_format not in ("markdown", "plain"):
        output_format = "markdown"

    max_packages = data.get("max_packages_shown")
    if max_packages is not None:
        max_packages = int(max_packages)

    return DigestConfig(
        min_severity=min_severity,
        include_safe=include_safe,
        output_format=output_format,
        max_packages_shown=max_packages,
    )
