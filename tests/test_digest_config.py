"""Tests for depwatch.digest_config."""

import pytest

from depwatch.severity_classifier import Severity
from depwatch.digest_config import DigestConfig, config_from_env, config_from_dict


def test_config_from_dict_defaults():
    cfg = config_from_dict({})
    assert cfg.min_severity == Severity.LOW
    assert cfg.include_safe is False
    assert cfg.output_format == "markdown"
    assert cfg.max_packages_shown is None


def test_config_from_dict_sets_min_severity():
    cfg = config_from_dict({"min_severity": "critical"})
    assert cfg.min_severity == Severity.CRITICAL


def test_config_from_dict_sets_include_safe():
    cfg = config_from_dict({"include_safe": True})
    assert cfg.include_safe is True


def test_config_from_dict_sets_output_format_plain():
    cfg = config_from_dict({"output_format": "plain"})
    assert cfg.output_format == "plain"


def test_config_from_dict_invalid_format_falls_back():
    cfg = config_from_dict({"output_format": "html"})
    assert cfg.output_format == "markdown"


def test_config_from_dict_sets_max_packages():
    cfg = config_from_dict({"max_packages_shown": 5})
    assert cfg.max_packages_shown == 5


def test_config_from_dict_unknown_severity_falls_back():
    cfg = config_from_dict({"min_severity": "extreme"})
    assert cfg.min_severity == Severity.LOW


def test_config_from_env_defaults(monkeypatch):
    monkeypatch.delenv("DEPWATCH_DIGEST_MIN_SEVERITY", raising=False)
    monkeypatch.delenv("DEPWATCH_DIGEST_INCLUDE_SAFE", raising=False)
    monkeypatch.delenv("DEPWATCH_DIGEST_FORMAT", raising=False)
    monkeypatch.delenv("DEPWATCH_DIGEST_MAX_PACKAGES", raising=False)
    cfg = config_from_env()
    assert cfg.min_severity == Severity.LOW
    assert cfg.include_safe is False
    assert cfg.output_format == "markdown"
    assert cfg.max_packages_shown is None


def test_config_from_env_reads_severity(monkeypatch):
    monkeypatch.setenv("DEPWATCH_DIGEST_MIN_SEVERITY", "high")
    cfg = config_from_env()
    assert cfg.min_severity == Severity.HIGH


def test_config_from_env_reads_include_safe(monkeypatch):
    monkeypatch.setenv("DEPWATCH_DIGEST_INCLUDE_SAFE", "true")
    cfg = config_from_env()
    assert cfg.include_safe is True


def test_config_from_env_reads_max_packages(monkeypatch):
    monkeypatch.setenv("DEPWATCH_DIGEST_MAX_PACKAGES", "10")
    cfg = config_from_env()
    assert cfg.max_packages_shown == 10


def test_config_from_env_invalid_max_packages_ignored(monkeypatch):
    monkeypatch.setenv("DEPWATCH_DIGEST_MAX_PACKAGES", "abc")
    cfg = config_from_env()
    assert cfg.max_packages_shown is None
