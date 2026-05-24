"""Configuration helpers for the PR labeler."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from depwatch.severity_classifier import Severity


@dataclass
class LabelerConfig:
    """Controls which labels are applied and under what conditions."""

    enabled: bool = True
    # Extra static labels always added when any breaking change is found
    extra_breaking_labels: List[str] = field(default_factory=list)
    # Override the default severity -> label mapping
    severity_label_overrides: Dict[str, str] = field(default_factory=dict)
    # Minimum severity required before any label is applied
    min_severity: Severity = Severity.LOW


def _parse_severity(value: str) -> Severity:
    try:
        return Severity[value.upper()]
    except KeyError:
        return Severity.LOW


def config_from_env() -> LabelerConfig:
    """Build a :class:`LabelerConfig` from environment variables.

    Recognised variables:
    - ``DEPWATCH_LABELER_ENABLED`` – ``"false"`` disables labeling entirely.
    - ``DEPWATCH_LABELER_EXTRA_LABELS`` – comma-separated list of extra labels.
    - ``DEPWATCH_LABELER_MIN_SEVERITY`` – one of ``LOW``, ``MEDIUM``, ``HIGH``, ``CRITICAL``.
    """
    enabled = os.environ.get("DEPWATCH_LABELER_ENABLED", "true").lower() != "false"
    raw_extra = os.environ.get("DEPWATCH_LABELER_EXTRA_LABELS", "")
    extra = [lbl.strip() for lbl in raw_extra.split(",") if lbl.strip()]
    min_sev = _parse_severity(os.environ.get("DEPWATCH_LABELER_MIN_SEVERITY", "LOW"))
    return LabelerConfig(enabled=enabled, extra_breaking_labels=extra, min_severity=min_sev)


def config_from_dict(data: dict) -> LabelerConfig:
    """Build a :class:`LabelerConfig` from a plain dictionary (e.g. parsed YAML)."""
    enabled = bool(data.get("enabled", True))
    extra = list(data.get("extra_breaking_labels", []))
    overrides = dict(data.get("severity_label_overrides", {}))
    min_sev = _parse_severity(str(data.get("min_severity", "LOW")))
    return LabelerConfig(
        enabled=enabled,
        extra_breaking_labels=extra,
        severity_label_overrides=overrides,
        min_severity=min_sev,
    )
