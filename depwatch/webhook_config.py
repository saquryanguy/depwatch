"""Convenience helpers for loading WebhookConfig from various sources."""

from __future__ import annotations

from typing import Any, Dict, Optional

from depwatch.webhook_notifier import WebhookConfig


def config_from_dict(data: Dict[str, Any]) -> Optional[WebhookConfig]:
    """Build a WebhookConfig from a plain dict (e.g. parsed YAML/JSON config).

    Returns None if 'url' is absent or empty.
    """
    url = str(data.get("url", "")).strip()
    if not url:
        return None

    secret: Optional[str] = data.get("secret") or None
    if secret is not None:
        secret = str(secret).strip() or None

    raw_timeout = data.get("timeout", 10)
    try:
        timeout = int(raw_timeout)
    except (TypeError, ValueError):
        timeout = 10

    return WebhookConfig(url=url, secret=secret, timeout=timeout)


def merge_configs(
    env_config: Optional[WebhookConfig],
    dict_config: Optional[WebhookConfig],
) -> Optional[WebhookConfig]:
    """Return the first non-None config, preferring env over dict."""
    return env_config if env_config is not None else dict_config
