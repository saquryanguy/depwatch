"""Tests for depwatch.diff_summary_config."""
from __future__ import annotations

import pytest

from depwatch.severity_classifier import Severity
from depwatch.diff_summary_config import (
    DiffSummaryConfig,
    config_from_env,
    config_from_dict,
)


def test_config_from_dict_defaults():
    cfg = config_from_dict({})
    assert cfg.min_severity is None
    assert cfg.include_safe is True
    assert cfg.max_headline_length == 120
    assert cfg.only_packages == []


def test_config_from_dict_sets_min_severity():
    cfg = config_from_dict({"min_severity": "HIGH"})
    assert cfg.min_severity == Severity.HIGH


def test_config_from_dict_invalid_severity_returns_none():
    cfg = config_from_dict({"min_severity": "INVALID"})
    assert cfg.min_severity is None


def test_config_from_dict_sets_include_safe_false():
    cfg = config_from_dict({"include_safe": False})
    assert cfg.include_safe is False


def test_config_from_dict_include_safe_false_string():
    cfg = config_from_dict({"include_safe": "false"})
    assert cfg.include_safe is False


def test_config_from_dict_sets_max_headline_length():
    cfg = config_from_dict({"max_headline_length": 80})
    assert cfg.max_headline_length == 80


def test_config_from_dict_invalid_max_length_falls_back():
    cfg = config_from_dict({"max_headline_length": "bad"})
    assert cfg.max_headline_length == 120


def test_config_from_dict_sets_only_packages_list():
    cfg = config_from_dict({"only_packages": ["requests", "flask"]})
    assert "requests" in cfg.only_packages
    assert "flask" in cfg.only_packages


def test_config_from_dict_sets_only_packages_csv_string():
    cfg = config_from_dict({"only_packages": "requests,flask"})
    assert "requests" in cfg.only_packages
    assert "flask" in cfg.only_packages


def test_config_from_env_defaults(monkeypatch):
    for key in [
        "DEPWATCH_SUMMARY_MIN_SEVERITY",
        "DEPWATCH_SUMMARY_INCLUDE_SAFE",
        "DEPWATCH_SUMMARY_MAX_HEADLINE_LENGTH",
        "DEPWATCH_SUMMARY_ONLY_PACKAGES",
    ]:
        monkeypatch.delenv(key, raising=False)
    cfg = config_from_env()
    assert cfg.min_severity is None
    assert cfg.include_safe is True
    assert cfg.max_headline_length == 120
    assert cfg.only_packages == []


def test_config_from_env_sets_min_severity(monkeypatch):
    monkeypatch.setenv("DEPWATCH_SUMMARY_MIN_SEVERITY", "CRITICAL")
    cfg = config_from_env()
    assert cfg.min_severity == Severity.CRITICAL


def test_config_from_env_include_safe_false(monkeypatch):
    monkeypatch.setenv("DEPWATCH_SUMMARY_INCLUDE_SAFE", "false")
    cfg = config_from_env()
    assert cfg.include_safe is False


def test_config_from_env_only_packages(monkeypatch):
    monkeypatch.setenv("DEPWATCH_SUMMARY_ONLY_PACKAGES", "django,numpy")
    cfg = config_from_env()
    assert "django" in cfg.only_packages
    assert "numpy" in cfg.only_packages
