"""Snapshot management for dependency state across runs."""
from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, List, Optional

DEFAULT_SNAPSHOT_DIR = ".depwatch_snapshots"


@dataclass
class DependencySnapshot:
    """Represents a point-in-time capture of resolved dependency versions."""

    run_id: str
    ref: str  # git ref / branch / tag
    packages: Dict[str, str]  # name -> version


def _snapshot_path(run_id: str, snapshot_dir: str = DEFAULT_SNAPSHOT_DIR) -> Path:
    return Path(snapshot_dir) / f"{run_id}.json"


def save_snapshot(
    snapshot: DependencySnapshot,
    snapshot_dir: str = DEFAULT_SNAPSHOT_DIR,
) -> Path:
    """Persist a snapshot to disk and return its path."""
    path = _snapshot_path(snapshot.run_id, snapshot_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(asdict(snapshot), indent=2))
    return path


def load_snapshot(
    run_id: str,
    snapshot_dir: str = DEFAULT_SNAPSHOT_DIR,
) -> Optional[DependencySnapshot]:
    """Load a snapshot by run_id, returning None if not found or corrupt."""
    path = _snapshot_path(run_id, snapshot_dir)
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text())
        return DependencySnapshot(**data)
    except (json.JSONDecodeError, TypeError):
        return None


def list_snapshots(snapshot_dir: str = DEFAULT_SNAPSHOT_DIR) -> List[str]:
    """Return sorted list of available run_ids."""
    directory = Path(snapshot_dir)
    if not directory.exists():
        return []
    return sorted(p.stem for p in directory.glob("*.json"))


def diff_snapshots(
    old: DependencySnapshot,
    new: DependencySnapshot,
) -> Dict[str, tuple]:
    """Return packages whose version changed between two snapshots.

    Returns a dict of {package: (old_version, new_version)}.
    Only includes packages present in both snapshots that have different versions,
    plus packages added in *new* (old_version will be None).
    """
    changes: Dict[str, tuple] = {}
    for pkg, new_ver in new.packages.items():
        old_ver = old.packages.get(pkg)
        if old_ver != new_ver:
            changes[pkg] = (old_ver, new_ver)
    return changes
