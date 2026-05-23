"""Configuration helpers for snapshot feature."""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional

from depwatch.snapshot import DEFAULT_SNAPSHOT_DIR


@dataclass
class SnapshotConfig:
    snapshot_dir: str = DEFAULT_SNAPSHOT_DIR
    run_id: Optional[str] = None
    ref: str = "HEAD"
    enabled: bool = True


def config_from_env() -> SnapshotConfig:
    """Build SnapshotConfig from environment variables."""
    return SnapshotConfig(
        snapshot_dir=os.environ.get("DEPWATCH_SNAPSHOT_DIR", DEFAULT_SNAPSHOT_DIR),
        run_id=os.environ.get("DEPWATCH_SNAPSHOT_RUN_ID") or None,
        ref=os.environ.get("GITHUB_SHA", os.environ.get("DEPWATCH_REF", "HEAD")),
        enabled=os.environ.get("DEPWATCH_SNAPSHOT_ENABLED", "true").lower()
        not in ("0", "false", "no"),
    )


def config_from_dict(data: dict) -> SnapshotConfig:
    """Build SnapshotConfig from a plain dict (e.g. parsed YAML/JSON config)."""
    enabled_raw = data.get("enabled", True)
    if isinstance(enabled_raw, str):
        enabled = enabled_raw.lower() not in ("0", "false", "no")
    else:
        enabled = bool(enabled_raw)

    return SnapshotConfig(
        snapshot_dir=data.get("snapshot_dir", DEFAULT_SNAPSHOT_DIR),
        run_id=data.get("run_id") or None,
        ref=data.get("ref", "HEAD"),
        enabled=enabled,
    )
