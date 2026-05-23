"""Configuration helpers for notification targets."""

from __future__ import annotations

import os
from typing import Dict, List

from depwatch.notification_router import NotificationTarget
from depwatch.severity_classifier import Severity


_SEVERITY_MAP: Dict[str, Severity] = {
    "low": Severity.LOW,
    "medium": Severity.MEDIUM,
    "high": Severity.HIGH,
    "critical": Severity.CRITICAL,
}

_TARGET_MAP: Dict[str, NotificationTarget] = {
    "stdout": NotificationTarget.STDOUT,
    "github": NotificationTarget.GITHUB,
    "slack": NotificationTarget.SLACK,
}


def _parse_severity(value: str, default: Severity = Severity.HIGH) -> Severity:
    return _SEVERITY_MAP.get(value.strip().lower(), default)


def _parse_targets(value: str) -> List[NotificationTarget]:
    targets: List[NotificationTarget] = []
    for part in value.split(","):
        key = part.strip().lower()
        if key in _TARGET_MAP:
            targets.append(_TARGET_MAP[key])
    return targets


def targets_from_env() -> List[NotificationTarget]:
    """Read notification targets from environment variables."""
    raw = os.environ.get("DEPWATCH_NOTIFY_TARGETS", "stdout")
    return _parse_targets(raw)


def targets_from_dict(cfg: Dict[str, str]) -> List[NotificationTarget]:
    """Build notification targets from a plain dict (e.g. parsed YAML/JSON)."""
    raw = cfg.get("notify_targets", "stdout")
    return _parse_targets(raw)


def min_severity_from_env(default: Severity = Severity.HIGH) -> Severity:
    """Read minimum notification severity from environment."""
    raw = os.environ.get("DEPWATCH_NOTIFY_MIN_SEVERITY", "")
    if not raw:
        return default
    return _parse_severity(raw, default)


def min_severity_from_dict(
    cfg: Dict[str, str],
    default: Severity = Severity.HIGH,
) -> Severity:
    """Read minimum notification severity from a config dict."""
    raw = cfg.get("notify_min_severity", "")
    if not raw:
        return default
    return _parse_severity(raw, default)
