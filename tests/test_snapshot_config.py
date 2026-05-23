"""Tests for depwatch.snapshot_config."""
import pytest

from depwatch.snapshot import DEFAULT_SNAPSHOT_DIR
from depwatch.snapshot_config import SnapshotConfig, config_from_dict, config_from_env


def test_config_from_dict_defaults():
    cfg = config_from_dict({})
    assert cfg.snapshot_dir == DEFAULT_SNAPSHOT_DIR
    assert cfg.run_id is None
    assert cfg.ref == "HEAD"
    assert cfg.enabled is True


def test_config_from_dict_sets_snapshot_dir():
    cfg = config_from_dict({"snapshot_dir": "/tmp/snaps"})
    assert cfg.snapshot_dir == "/tmp/snaps"


def test_config_from_dict_sets_run_id():
    cfg = config_from_dict({"run_id": "abc123"})
    assert cfg.run_id == "abc123"


def test_config_from_dict_empty_run_id_becomes_none():
    cfg = config_from_dict({"run_id": ""})
    assert cfg.run_id is None


def test_config_from_dict_disabled_string():
    for val in ("false", "0", "no"):
        cfg = config_from_dict({"enabled": val})
        assert cfg.enabled is False


def test_config_from_dict_enabled_bool_false():
    cfg = config_from_dict({"enabled": False})
    assert cfg.enabled is False


def test_config_from_dict_sets_ref():
    cfg = config_from_dict({"ref": "deadbeef"})
    assert cfg.ref == "deadbeef"


def test_config_from_env_defaults(monkeypatch):
    for key in (
        "DEPWATCH_SNAPSHOT_DIR",
        "DEPWATCH_SNAPSHOT_RUN_ID",
        "GITHUB_SHA",
        "DEPWATCH_REF",
        "DEPWATCH_SNAPSHOT_ENABLED",
    ):
        monkeypatch.delenv(key, raising=False)
    cfg = config_from_env()
    assert cfg.snapshot_dir == DEFAULT_SNAPSHOT_DIR
    assert cfg.run_id is None
    assert cfg.ref == "HEAD"
    assert cfg.enabled is True


def test_config_from_env_reads_snapshot_dir(monkeypatch):
    monkeypatch.setenv("DEPWATCH_SNAPSHOT_DIR", "/custom/snaps")
    cfg = config_from_env()
    assert cfg.snapshot_dir == "/custom/snaps"


def test_config_from_env_reads_github_sha(monkeypatch):
    monkeypatch.delenv("DEPWATCH_REF", raising=False)
    monkeypatch.setenv("GITHUB_SHA", "sha999")
    cfg = config_from_env()
    assert cfg.ref == "sha999"


def test_config_from_env_disabled(monkeypatch):
    monkeypatch.setenv("DEPWATCH_SNAPSHOT_ENABLED", "false")
    cfg = config_from_env()
    assert cfg.enabled is False
