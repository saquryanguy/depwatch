"""Configuration for the changelog diff tagger."""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import List, Optional

from depwatch.severity_classifier import Severity


@dataclass
class TaggerConfig:
    enabled: bool = True
    extra_tags: List[str] = field(default_factory=list)
    min_severity: Optional[Severity] = None
    skip_safe: bool = False


def _parse_severity(value: str) -> Optional[Severity]:
    mapping = {
        "critical": Severity.CRITICAL,
        "high": Severity.HIGH,
        "medium": Severity.MEDIUM,
        "low": Severity.LOW,
        "safe": Severity.SAFE,
    }
    return mapping.get(value.strip().lower())


def _parse_csv(value: str) -> List[str]:
    return [v.strip() for v in value.split(",") if v.strip()]


def config_from_env() -> TaggerConfig:
    enabled = os.environ.get("DEPWATCH_TAGGER_ENABLED", "true").lower() != "false"
    extra_tags = _parse_csv(os.environ.get("DEPWATCH_TAGGER_EXTRA_TAGS", ""))
    min_sev_raw = os.environ.get("DEPWATCH_TAGGER_MIN_SEVERITY", "")
    min_severity = _parse_severity(min_sev_raw) if min_sev_raw else None
    skip_safe = os.environ.get("DEPWATCH_TAGGER_SKIP_SAFE", "false").lower() == "true"
    return TaggerConfig(
        enabled=enabled,
        extra_tags=extra_tags,
        min_severity=min_severity,
        skip_safe=skip_safe,
    )


def config_from_dict(data: dict) -> TaggerConfig:
    enabled = str(data.get("enabled", "true")).lower() != "false"
    extra_raw = data.get("extra_tags", "")
    if isinstance(extra_raw, list):
        extra_tags = [str(t).strip() for t in extra_raw if str(t).strip()]
    else:
        extra_tags = _parse_csv(str(extra_raw))
    min_sev_raw = data.get("min_severity", "")
    min_severity = _parse_severity(str(min_sev_raw)) if min_sev_raw else None
    skip_safe = str(data.get("skip_safe", "false")).lower() == "true"
    return TaggerConfig(
        enabled=enabled,
        extra_tags=extra_tags,
        min_severity=min_severity,
        skip_safe=skip_safe,
    )
