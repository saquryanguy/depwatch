"""Configuration for the changelog diff archiver."""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional

_DEFAULT_ARCHIVE_DIR = ".depwatch/archive"


@dataclass
class ArchiveConfig:
    enabled: bool = True
    archive_dir: str = _DEFAULT_ARCHIVE_DIR
    run_id: Optional[str] = None


def config_from_env() -> ArchiveConfig:
    """Build ArchiveConfig from environment variables."""
    enabled_raw = os.environ.get("DEPWATCH_ARCHIVE_ENABLED", "true").lower()
    enabled = enabled_raw not in ("false", "0", "no")
    archive_dir = os.environ.get("DEPWATCH_ARCHIVE_DIR", _DEFAULT_ARCHIVE_DIR)
    run_id = os.environ.get("DEPWATCH_RUN_ID") or None
    return ArchiveConfig(enabled=enabled, archive_dir=archive_dir, run_id=run_id)


def config_from_dict(data: dict) -> ArchiveConfig:
    """Build ArchiveConfig from a plain dictionary (e.g. from YAML)."""
    enabled_raw = str(data.get("enabled", "true")).lower()
    enabled = enabled_raw not in ("false", "0", "no")
    archive_dir = data.get("archive_dir") or _DEFAULT_ARCHIVE_DIR
    run_id = data.get("run_id") or None
    return ArchiveConfig(enabled=enabled, archive_dir=archive_dir, run_id=run_id)
