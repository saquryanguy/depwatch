"""Tests for diff_group_config."""

from __future__ import annotations

import pytest

from depwatch.diff_group_config import (
    DiffGroupConfig,
    config_from_dict,
    config_from_env,
)
from depwatch.severity_classifier import Severity


def test_config_from_dict_defaults():
    cfg = config_from_dict({})
    assert isinstance(cfg, DiffGroupConfig)
    assert cfg.min_severity is None
    assert cfg.include_safe is True
    assert cfg.max_packages_per_group == 50


def test_config_from_dict_sets_min_severity():
    cfg = config_from_dict({"min_severity": "HIGH"})
    assert cfg.min_severity == Severity.HIGH


def test_config_from_dict_invalid_severity_returns_none():
    cfg = config_from_dict({"min_severity": "BOGUS"})
    assert cfg.min_severity is None


def test_config_from_dict_sets_include_safe_false():
    cfg = config_from_dict({"include_safe": False})
    assert cfg.include_safe is False


def test_config_from_dict_include_safe_false_string():
    cfg = config_from_dict({"include_safe": "false"})
    assert cfg.include_safe is False


def test_config_from_dict_sets_max_packages():
    cfg = config_from_dict({"max_packages_per_group": 10})
    assert cfg.max_packages_per_group == 10


def test_config_from_dict_invalid_max_packages_falls_back():
    cfg = config_from_dict({"max_packages_per_group": "not_a_number"})
    assert cfg.max_packages_per_group == 50


def test_config_from_env_defaults(monkeypatch):
    monkeypatch.delenv("DEPWATCH_GROUP_MIN_SEVERITY", raising=False)
    monkeypatch.delenv("DEPWATCH_GROUP_INCLUDE_SAFE", raising=False)
    monkeypatch.delenv("DEPWATCH_GROUP_MAX_PACKAGES", raising=False)
    cfg = config_from_env()
    assert cfg.min_severity is None
    assert cfg.include_safe is True
    assert cfg.max_packages_per_group == 50


def test_config_from_env_sets_min_severity(monkeypatch):
    monkeypatch.setenv("DEPWATCH_GROUP_MIN_SEVERITY", "CRITICAL")
    cfg = config_from_env()
    assert cfg.min_severity == Severity.CRITICAL


def test_config_from_env_sets_include_safe_false(monkeypatch):
    monkeypatch.setenv("DEPWATCH_GROUP_INCLUDE_SAFE", "false")
    cfg = config_from_env()
    assert cfg.include_safe is False


def test_config_from_env_sets_max_packages(monkeypatch):
    monkeypatch.setenv("DEPWATCH_GROUP_MAX_PACKAGES", "25")
    cfg = config_from_env()
    assert cfg.max_packages_per_group == 25


def test_config_from_env_invalid_max_packages_falls_back(monkeypatch):
    monkeypatch.setenv("DEPWATCH_GROUP_MAX_PACKAGES", "abc")
    cfg = config_from_env()
    assert cfg.max_packages_per_group == 50
