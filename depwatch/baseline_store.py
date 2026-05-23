"""Persist and retrieve dependency baselines across pipeline runs."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Dict, Optional

_DEFAULT_PATH = Path(".depwatch_baseline.json")


def _baseline_path() -> Path:
    env = os.environ.get("DEPWATCH_BASELINE_FILE")
    return Path(env) if env else _DEFAULT_PATH


def load_baseline(path: Optional[Path] = None) -> Dict[str, str]:
    """Return the stored baseline as {package: version} or {} if missing."""
    target = path or _baseline_path()
    if not target.exists():
        return {}
    try:
        data = json.loads(target.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            return {}
        return {str(k): str(v) for k, v in data.items()}
    except (json.JSONDecodeError, OSError):
        return {}


def save_baseline(deps: Dict[str, str], path: Optional[Path] = None) -> None:
    """Persist *deps* as the new baseline, overwriting any previous file."""
    target = path or _baseline_path()
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(deps, indent=2, sort_keys=True), encoding="utf-8")


def diff_from_baseline(
    current: Dict[str, str],
    baseline: Optional[Dict[str, str]] = None,
    path: Optional[Path] = None,
) -> Dict[str, tuple[str, str]]:
    """Return packages whose version changed between *baseline* and *current*.

    Returns a mapping of ``{package: (old_version, new_version)}``.
    New packages (not present in baseline) are included with old_version="".
    """
    stored = baseline if baseline is not None else load_baseline(path)
    changed: Dict[str, tuple[str, str]] = {}
    for pkg, ver in current.items():
        old = stored.get(pkg, "")
        if old != ver:
            changed[pkg] = (old, ver)
    return changed
