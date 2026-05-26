"""Tests for tagger_config."""
from __future__ import annotations

import pytest

from depwatch.severity_classifier import Severity
from depwatch.tagger_config import TaggerConfig, config_from_dict, config_from_env


def test_config_from_dict_defaults():
    cfg = config_from_dict({})
    assert cfg.enabled is True
    assert cfg.extra_tags == []
    assert cfg.min_severity is None
    assert cfg.skip_safe is False


def test_config_from_dict_sets_enabled_false():
    cfg = config_from_dict({"enabled": "false"})
    assert cfg.enabled is False


def test_config_from_dict_sets_extra_tags_csv():
    cfg = config_from_dict({"extra_tags": "foo, bar, baz"})
    assert cfg.extra_tags == ["foo", "bar", "baz"]


def test_config_from_dict_sets_extra_tags_list():
    cfg = config_from_dict({"extra_tags": ["alpha", "beta"]})
    assert cfg.extra_tags == ["alpha", "beta"]


def test_config_from_dict_sets_min_severity_high():
    cfg = config_from_dict({"min_severity": "high"})
    assert cfg.min_severity == Severity.HIGH


def test_config_from_dict_invalid_severity_returns_none():
    cfg = config_from_dict({"min_severity": "unknown"})
    assert cfg.min_severity is None


def test_config_from_dict_sets_skip_safe_true():
    cfg = config_from_dict({"skip_safe": "true"})
    assert cfg.skip_safe is True


def test_config_from_dict_skip_safe_false_string():
    cfg = config_from_dict({"skip_safe": "false"})
    assert cfg.skip_safe is False


def test_config_from_env_defaults(monkeypatch):
    monkeypatch.delenv("DEPWATCH_TAGGER_ENABLED", raising=False)
    monkeypatch.delenv("DEPWATCH_TAGGER_EXTRA_TAGS", raising=False)
    monkeypatch.delenv("DEPWATCH_TAGGER_MIN_SEVERITY", raising=False)
    monkeypatch.delenv("DEPWATCH_TAGGER_SKIP_SAFE", raising=False)
    cfg = config_from_env()
    assert cfg.enabled is True
    assert cfg.extra_tags == []
    assert cfg.min_severity is None
    assert cfg.skip_safe is False


def test_config_from_env_sets_enabled_false(monkeypatch):
    monkeypatch.setenv("DEPWATCH_TAGGER_ENABLED", "false")
    cfg = config_from_env()
    assert cfg.enabled is False


def test_config_from_env_sets_extra_tags(monkeypatch):
    monkeypatch.setenv("DEPWATCH_TAGGER_EXTRA_TAGS", "ci, nightly")
    cfg = config_from_env()
    assert cfg.extra_tags == ["ci", "nightly"]


def test_config_from_env_sets_min_severity_critical(monkeypatch):
    monkeypatch.setenv("DEPWATCH_TAGGER_MIN_SEVERITY", "critical")
    cfg = config_from_env()
    assert cfg.min_severity == Severity.CRITICAL


def test_config_from_env_sets_skip_safe(monkeypatch):
    monkeypatch.setenv("DEPWATCH_TAGGER_SKIP_SAFE", "true")
    cfg = config_from_env()
    assert cfg.skip_safe is True
