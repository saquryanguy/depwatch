"""Tests for depwatch.export_config."""
from __future__ import annotations

import pytest

from depwatch.export_config import config_from_dict, config_from_env


def test_config_from_dict_defaults():
    cfg = config_from_dict({})
    assert cfg.output_format == "markdown"
    assert cfg.output_path is None
    assert cfg.include_safe is False


def test_config_from_dict_sets_format_plain():
    cfg = config_from_dict({"output_format": "plain"})
    assert cfg.output_format == "plain"


def test_config_from_dict_sets_format_json():
    cfg = config_from_dict({"output_format": "json"})
    assert cfg.output_format == "json"


def test_config_from_dict_invalid_format_falls_back():
    cfg = config_from_dict({"output_format": "html"})
    assert cfg.output_format == "markdown"


def test_config_from_dict_sets_output_path():
    cfg = config_from_dict({"output_path": "/tmp/out.md"})
    assert cfg.output_path == "/tmp/out.md"


def test_config_from_dict_empty_path_is_none():
    cfg = config_from_dict({"output_path": ""})
    assert cfg.output_path is None


def test_config_from_dict_include_safe_true():
    cfg = config_from_dict({"include_safe": True})
    assert cfg.include_safe is True


def test_config_from_env_defaults(monkeypatch):
    monkeypatch.delenv("DEPWATCH_EXPORT_FORMAT", raising=False)
    monkeypatch.delenv("DEPWATCH_EXPORT_PATH", raising=False)
    monkeypatch.delenv("DEPWATCH_EXPORT_INCLUDE_SAFE", raising=False)
    cfg = config_from_env()
    assert cfg.output_format == "markdown"
    assert cfg.output_path is None
    assert cfg.include_safe is False


def test_config_from_env_sets_format(monkeypatch):
    monkeypatch.setenv("DEPWATCH_EXPORT_FORMAT", "json")
    cfg = config_from_env()
    assert cfg.output_format == "json"


def test_config_from_env_invalid_format_falls_back(monkeypatch):
    monkeypatch.setenv("DEPWATCH_EXPORT_FORMAT", "csv")
    cfg = config_from_env()
    assert cfg.output_format == "markdown"


def test_config_from_env_include_safe_true(monkeypatch):
    monkeypatch.setenv("DEPWATCH_EXPORT_INCLUDE_SAFE", "true")
    cfg = config_from_env()
    assert cfg.include_safe is True


def test_config_from_env_include_safe_1(monkeypatch):
    monkeypatch.setenv("DEPWATCH_EXPORT_INCLUDE_SAFE", "1")
    cfg = config_from_env()
    assert cfg.include_safe is True
