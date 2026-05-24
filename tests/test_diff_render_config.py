"""Tests for diff_render_config."""
from __future__ import annotations

import pytest

from depwatch.diff_render_config import (
    DiffRenderConfig,
    config_from_dict,
    config_from_env,
)
from depwatch.severity_classifier import Severity


# --- config_from_dict ---

def test_config_from_dict_defaults():
    cfg = config_from_dict({})
    assert cfg.output_format == "markdown"
    assert cfg.min_severity is None
    assert cfg.include_safe is True
    assert cfg.max_lines_per_package == 50


def test_config_from_dict_sets_format_plain():
    cfg = config_from_dict({"output_format": "plain"})
    assert cfg.output_format == "plain"


def test_config_from_dict_invalid_format_falls_back():
    cfg = config_from_dict({"output_format": "xml"})
    assert cfg.output_format == "markdown"


def test_config_from_dict_sets_min_severity():
    cfg = config_from_dict({"min_severity": "HIGH"})
    assert cfg.min_severity == Severity.HIGH


def test_config_from_dict_invalid_severity_returns_none():
    cfg = config_from_dict({"min_severity": "EXTREME"})
    assert cfg.min_severity is None


def test_config_from_dict_sets_include_safe_false():
    cfg = config_from_dict({"include_safe": False})
    assert cfg.include_safe is False


def test_config_from_dict_sets_max_lines():
    cfg = config_from_dict({"max_lines_per_package": 20})
    assert cfg.max_lines_per_package == 20


def test_config_from_dict_invalid_max_lines_falls_back():
    cfg = config_from_dict({"max_lines_per_package": "lots"})
    assert cfg.max_lines_per_package == 50


# --- config_from_env ---

def test_config_from_env_defaults(monkeypatch):
    for key in (
        "DEPWATCH_RENDER_FORMAT",
        "DEPWATCH_RENDER_MIN_SEVERITY",
        "DEPWATCH_RENDER_INCLUDE_SAFE",
        "DEPWATCH_RENDER_MAX_LINES",
    ):
        monkeypatch.delenv(key, raising=False)
    cfg = config_from_env()
    assert cfg.output_format == "markdown"
    assert cfg.min_severity is None
    assert cfg.include_safe is True
    assert cfg.max_lines_per_package == 50


def test_config_from_env_sets_format(monkeypatch):
    monkeypatch.setenv("DEPWATCH_RENDER_FORMAT", "plain")
    cfg = config_from_env()
    assert cfg.output_format == "plain"


def test_config_from_env_sets_min_severity(monkeypatch):
    monkeypatch.setenv("DEPWATCH_RENDER_MIN_SEVERITY", "MEDIUM")
    cfg = config_from_env()
    assert cfg.min_severity == Severity.MEDIUM


def test_config_from_env_include_safe_false(monkeypatch):
    monkeypatch.setenv("DEPWATCH_RENDER_INCLUDE_SAFE", "false")
    cfg = config_from_env()
    assert cfg.include_safe is False


def test_config_from_env_invalid_max_lines_falls_back(monkeypatch):
    monkeypatch.setenv("DEPWATCH_RENDER_MAX_LINES", "abc")
    cfg = config_from_env()
    assert cfg.max_lines_per_package == 50
