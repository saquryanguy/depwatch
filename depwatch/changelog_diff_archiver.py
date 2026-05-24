"""Archive changelog diffs to disk for historical reference."""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

from depwatch.changelog_diff import ChangelogDiff

_DEFAULT_ARCHIVE_DIR = ".depwatch/archive"


@dataclass
class ArchiveEntry:
    package: str
    old_version: str
    new_version: str
    lines: List[str]
    archived_at: str
    run_id: Optional[str] = None


@dataclass
class ArchiveResult:
    package: str
    path: str
    success: bool
    error: Optional[str] = None


def _archive_path(archive_dir: str, package: str, run_id: Optional[str]) -> Path:
    base = Path(archive_dir)
    stamp = run_id or datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return base / f"{package}__{stamp}.json"


def archive_diff(diff: ChangelogDiff, archive_dir: str = _DEFAULT_ARCHIVE_DIR,
                run_id: Optional[str] = None) -> ArchiveResult:
    """Persist a single ChangelogDiff to an archive JSON file."""
    path = _archive_path(archive_dir, diff.package, run_id)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        entry = ArchiveEntry(
            package=diff.package,
            old_version=diff.old_version,
            new_version=diff.new_version,
            lines=diff.lines,
            archived_at=datetime.now(timezone.utc).isoformat(),
            run_id=run_id,
        )
        path.write_text(json.dumps(entry.__dict__, indent=2), encoding="utf-8")
        return ArchiveResult(package=diff.package, path=str(path), success=True)
    except OSError as exc:
        return ArchiveResult(package=diff.package, path=str(path), success=False, error=str(exc))


def archive_diffs(diffs: List[ChangelogDiff], archive_dir: str = _DEFAULT_ARCHIVE_DIR,
                 run_id: Optional[str] = None) -> List[ArchiveResult]:
    """Archive a list of ChangelogDiff objects, returning one result per diff."""
    return [archive_diff(d, archive_dir=archive_dir, run_id=run_id) for d in diffs]


def load_archive_entry(path: str) -> Optional[ArchiveEntry]:
    """Load a previously archived entry from disk."""
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        return ArchiveEntry(**data)
    except (OSError, KeyError, TypeError, json.JSONDecodeError):
        return None
