"""Read and query archived changelog diffs."""
from __future__ import annotations

import json
from pathlib import Path
from typing import List, Optional

from depwatch.changelog_diff_archiver import ArchiveEntry, load_archive_entry


def list_archive_files(archive_dir: str) -> List[Path]:
    """Return all .json archive files sorted by name (chronological by stamp)."""
    base = Path(archive_dir)
    if not base.exists():
        return []
    return sorted(base.glob("*.json"))


def load_all_entries(archive_dir: str) -> List[ArchiveEntry]:
    """Load every valid archive entry from *archive_dir*."""
    entries: List[ArchiveEntry] = []
    for path in list_archive_files(archive_dir):
        entry = load_archive_entry(str(path))
        if entry is not None:
            entries.append(entry)
    return entries


def entries_for_package(archive_dir: str, package: str) -> List[ArchiveEntry]:
    """Return all archived entries for a specific package name."""
    normalised = package.lower().replace("-", "_")
    return [
        e for e in load_all_entries(archive_dir)
        if e.package.lower().replace("-", "_") == normalised
    ]


def latest_entry(archive_dir: str, package: str) -> Optional[ArchiveEntry]:
    """Return the most recent archive entry for *package*, or None."""
    entries = entries_for_package(archive_dir, package)
    return entries[-1] if entries else None
