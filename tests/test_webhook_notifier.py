"""Tests for depwatch.webhook_notifier."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest

from depwatch.severity_classifier import Severity
from depwatch.severity_report import SeverityReport, build_severity_report
from depwatch.webhook_notifier import (
    WebhookConfig,
    build_webhook_payload,
    config_from_env,
    send_webhook,
)


def _make_report(lines=None):
    return build_severity_report(
        package="requests",
        from_version="2.27.0",
        to_version="2.28.0",
        lines=lines or [],
    )


# --- config_from_env ---

def test_config_from_env_missing_url_returns_none(monkeypatch):
    monkeypatch.delenv("DEPWATCH_WEBHOOK_URL", raising=False)
    assert config_from_env() is None


def test_config_from_env_empty_url_returns_none(monkeypatch):
    monkeypatch.setenv("DEPWATCH_WEBHOOK_URL", "   ")
    assert config_from_env() is None


def test_config_from_env_sets_url(monkeypatch):
    monkeypatch.setenv("DEPWATCH_WEBHOOK_URL", "https://example.com/hook")
    monkeypatch.delenv("DEPWATCH_WEBHOOK_SECRET", raising=False)
    cfg = config_from_env()
    assert cfg is not None
    assert cfg.url == "https://example.com/hook"


def test_config_from_env_sets_secret(monkeypatch):
    monkeypatch.setenv("DEPWATCH_WEBHOOK_URL", "https://example.com/hook")
    monkeypatch.setenv("DEPWATCH_WEBHOOK_SECRET", "mysecret")
    cfg = config_from_env()
    assert cfg.secret == "mysecret"


def test_config_from_env_invalid_timeout_falls_back(monkeypatch):
    monkeypatch.setenv("DEPWATCH_WEBHOOK_URL", "https://example.com/hook")
    monkeypatch.setenv("DEPWATCH_WEBHOOK_TIMEOUT", "bad")
    cfg = config_from_env()
    assert cfg.timeout == 10


# --- build_webhook_payload ---

def test_build_webhook_payload_package(monkeypatch):
    report = _make_report()
    payload = build_webhook_payload(report)
    assert payload["package"] == "requests"


def test_build_webhook_payload_versions(monkeypatch):
    report = _make_report()
    payload = build_webhook_payload(report)
    assert payload["from_version"] == "2.27.0"
    assert payload["to_version"] == "2.28.0"


def test_build_webhook_payload_breaking_count():
    report = _make_report(["Removed support for Python 3.6", "safe line"])
    payload = build_webhook_payload(report)
    assert payload["breaking_count"] == len(report.annotated_lines)


def test_build_webhook_payload_severity_is_string():
    report = _make_report()
    payload = build_webhook_payload(report)
    assert isinstance(payload["highest_severity"], str)


# --- send_webhook ---

def test_send_webhook_returns_true_on_200():
    cfg = WebhookConfig(url="https://example.com/hook")
    report = _make_report()
    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_resp.__enter__ = lambda s: s
    mock_resp.__exit__ = MagicMock(return_value=False)
    with patch("urllib.request.urlopen", return_value=mock_resp):
        assert send_webhook(cfg, report) is True


def test_send_webhook_returns_false_on_error():
    import urllib.error
    cfg = WebhookConfig(url="https://example.com/hook")
    report = _make_report()
    with patch("urllib.request.urlopen", side_effect=urllib.error.URLError("fail")):
        assert send_webhook(cfg, report) is False


def test_send_webhook_includes_secret_header():
    cfg = WebhookConfig(url="https://example.com/hook", secret="tok")
    report = _make_report()
    captured = {}

    def fake_urlopen(req, timeout):
        captured["headers"] = dict(req.headers)
        mock_resp = MagicMock()
        mock_resp.status = 204
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)
        return mock_resp

    with patch("urllib.request.urlopen", side_effect=fake_urlopen):
        send_webhook(cfg, report)

    assert "X-depwatch-secret" in captured["headers"]
