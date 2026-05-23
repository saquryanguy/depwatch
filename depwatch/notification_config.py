"""Load notification routing configuration from environment variables or a dict."""

from __future__ import annotations

import os
from typing import Dict, List, Optional

from depwatch.severity_classifier import Severity
from depwatch.notification_router import NotificationTarget

_SEVERITY_MAP: Dict[str, Severity] = {
    "low": Severity.LOW,
    "medium": Severity.MEDIUM,
    "high": Severity.HIGH,
    "critical": Severity.CRITICAL,
}


def _parse_severity(value: str, default: Severity = Severity.HIGH) -> Severity:
    """Parse a severity string, returning *default* on unrecognised input."""
    return _SEVERITY_MAP.get(value.strip().lower(), default)


def targets_from_env() -> List[NotificationTarget]:
    """Build notification targets from environment variables.

    Recognised variables
    --------------------
    DEPWATCH_NOTIFY_STDOUT_MIN_SEVERITY  (default: low)
    DEPWATCH_NOTIFY_PR_COMMENT_MIN_SEVERITY  (default: high)
    DEPWATCH_NOTIFY_PR_COMMENT_ENABLED  (default: true)
    """
    targets: List[NotificationTarget] = []

    stdout_min = _parse_severity(
        os.environ.get("DEPWATCH_NOTIFY_STDOUT_MIN_SEVERITY", "low"),
        default=Severity.LOW,
    )
    targets.append(
        NotificationTarget(channel="stdout", min_severity=stdout_min, label="console")
    )

    pr_enabled = os.environ.get("DEPWATCH_NOTIFY_PR_COMMENT_ENABLED", "true").lower()
    if pr_enabled not in ("false", "0", "no"):
        pr_min = _parse_severity(
            os.environ.get("DEPWATCH_NOTIFY_PR_COMMENT_MIN_SEVERITY", "high"),
            default=Severity.HIGH,
        )
        targets.append(
            NotificationTarget(channel="pr_comment", min_severity=pr_min, label="pr")
        )

    return targets


def targets_from_dict(config: Dict[str, str]) -> List[NotificationTarget]:
    """Build notification targets from a plain dictionary (e.g. parsed YAML/JSON).

    Expected keys (all optional)
    ----------------------------
    stdout_min_severity      (default: low)
    pr_comment_enabled       (default: true)
    pr_comment_min_severity  (default: high)
    """
    targets: List[NotificationTarget] = []

    stdout_min = _parse_severity(config.get("stdout_min_severity", "low"), Severity.LOW)
    targets.append(
        NotificationTarget(channel="stdout", min_severity=stdout_min, label="console")
    )

    pr_enabled = str(config.get("pr_comment_enabled", "true")).lower()
    if pr_enabled not in ("false", "0", "no"):
        pr_min = _parse_severity(
            config.get("pr_comment_min_severity", "high"), Severity.HIGH
        )
        targets.append(
            NotificationTarget(channel="pr_comment", min_severity=pr_min, label="pr")
        )

    return targets
