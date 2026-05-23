"""Webhook notification support for depwatch alerts."""

from __future__ import annotations

import json
import os
import urllib.request
import urllib.error
from dataclasses import dataclass
from typing import Optional

from depwatch.severity_report import SeverityReport


@dataclass
class WebhookConfig:
    url: str
    secret: Optional[str] = None
    timeout: int = 10


def config_from_env() -> Optional[WebhookConfig]:
    """Build WebhookConfig from environment variables, or None if not configured."""
    url = os.environ.get("DEPWATCH_WEBHOOK_URL", "").strip()
    if not url:
        return None
    secret = os.environ.get("DEPWATCH_WEBHOOK_SECRET") or None
    try:
        timeout = int(os.environ.get("DEPWATCH_WEBHOOK_TIMEOUT", "10"))
    except ValueError:
        timeout = 10
    return WebhookConfig(url=url, secret=secret, timeout=timeout)


def build_webhook_payload(report: SeverityReport) -> dict:
    """Serialize a SeverityReport into a webhook JSON payload."""
    return {
        "package": report.package,
        "from_version": report.from_version,
        "to_version": report.to_version,
        "highest_severity": report.highest_severity.value,
        "breaking_count": len(report.annotated_lines),
        "lines": [
            {"text": line.text, "severity": line.severity.value}
            for line in report.annotated_lines
        ],
    }


def send_webhook(config: WebhookConfig, report: SeverityReport) -> bool:
    """POST the report payload to the configured webhook URL.

    Returns True on success (HTTP 2xx), False otherwise.
    """
    payload = build_webhook_payload(report)
    data = json.dumps(payload).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    if config.secret:
        headers["X-DepWatch-Secret"] = config.secret

    req = urllib.request.Request(
        config.url, data=data, headers=headers, method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=config.timeout) as resp:
            return 200 <= resp.status < 300
    except (urllib.error.URLError, OSError):
        return False
