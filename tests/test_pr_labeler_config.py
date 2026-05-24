"""Tests for depwatch.pr_labeler_config."""

from __future__ import annotations

import pytest

from depwatch.severity_classifier import Severity
from depwatch.pr_labeler_config import LabelerConfig, config_from_dict, config_from_env


# ---------------------------------------------------------------------------
# config_from_dict
# ---------------------------------------------------------------------------

def test_config_from_dict_defaults():
    cfg = config_from_dict({})
    assert cfg.enabled is True
    assert cfg.extra_breaking_labels == []
    assert cfg.severity_label_overrides == {}
    assert cfg.min_severity == Severity.LOW


def test_config_from_dict_sets_enabled_false():
    cfg = config_from_dict({"enabled": False})
    assert cfg.enabled is False


def test_config_from_dict_sets_extra_labels():
    cfg = config_from_dict({"extra_breaking_labels": ["needs-review", "breaking"]})
    assert cfg.extra_breaking_labels == ["needs-review", "breaking"]


def test_config_from_dict_sets_overrides():
    cfg = config_from_dict({"severity_label_overrides": {"CRITICAL": "sev-critical"}})
    assert cfg.severity_label_overrides == {"CRITICAL": "sev-critical"}


def test_config_from_dict_sets_min_severity():
    cfg = config_from_dict({"min_severity": "HIGH"})
    assert cfg.min_severity == Severity.HIGH


def test_config_from_dict_invalid_severity_falls_back():
    cfg = config_from_dict({"min_severity": "UNKNOWN"})
    assert cfg.min_severity == Severity.LOW


# ---------------------------------------------------------------------------
# config_from_env
# ---------------------------------------------------------------------------

def test_config_from_env_defaults(monkeypatch):
    monkeypatch.delenv("DEPWATCH_LABELER_ENABLED", raising=False)
    monkeypatch.delenv("DEPWATCH_LABELER_EXTRA_LABELS", raising=False)
    monkeypatch.delenv("DEPWATCH_LABELER_MIN_SEVERITY", raising=False)
    cfg = config_from_env()
    assert cfg.enabled is True
    assert cfg.extra_breaking_labels == []
    assert cfg.min_severity == Severity.LOW


def test_config_from_env_disabled(monkeypatch):
    monkeypatch.setenv("DEPWATCH_LABELER_ENABLED", "false")
    cfg = config_from_env()
    assert cfg.enabled is False


def test_config_from_env_extra_labels(monkeypatch):
    monkeypatch.setenv("DEPWATCH_LABELER_EXTRA_LABELS", "needs-review, breaking")
    cfg = config_from_env()
    assert cfg.extra_breaking_labels == ["needs-review", "breaking"]


def test_config_from_env_min_severity(monkeypatch):
    monkeypatch.setenv("DEPWATCH_LABELER_MIN_SEVERITY", "CRITICAL")
    cfg = config_from_env()
    assert cfg.min_severity == Severity.CRITICAL
