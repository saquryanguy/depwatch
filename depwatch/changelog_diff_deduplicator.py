"""Deduplicates changelog diff lines across multiple package reports."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict, Optional

from depwatch.changelog_diff import ChangelogDiff


@dataclass
class DeduplicatedDiff:
    """A changelog diff with duplicate lines removed."""
    diff: ChangelogDiff
    original_count: int
    deduplicated_count: int
    removed_count: int

    @property
    def package(self) -> str:
        return self.diff.package

    @property
    def dedup_ratio(self) -> float:
        if self.original_count == 0:
            return 0.0
        return self.removed_count / self.original_count


@dataclass
class DeduplicationReport:
    entries: List[DeduplicatedDiff] = field(default_factory=list)

    @property
    def total_removed(self) -> int:
        return sum(e.removed_count for e in self.entries)

    @property
    def packages(self) -> List[str]:
        return [e.package for e in self.entries]


def _normalize_line(line: str) -> str:
    """Normalize a line for deduplication comparison."""
    return line.strip().lower()


def deduplicate_diff(diff: ChangelogDiff) -> DeduplicatedDiff:
    """Remove duplicate lines from a single changelog diff."""
    original_lines = diff.lines
    original_count = len(original_lines)

    seen: Dict[str, bool] = {}
    unique_lines: List[str] = []
    for line in original_lines:
        key = _normalize_line(line)
        if key and key not in seen:
            seen[key] = True
            unique_lines.append(line)
        elif not key:
            unique_lines.append(line)

    removed = original_count - len(unique_lines)
    deduped_diff = ChangelogDiff(
        package=diff.package,
        old_version=diff.old_version,
        new_version=diff.new_version,
        lines=unique_lines,
    )
    return DeduplicatedDiff(
        diff=deduped_diff,
        original_count=original_count,
        deduplicated_count=len(unique_lines),
        removed_count=removed,
    )


def deduplicate_diffs(
    diffs: List[ChangelogDiff],
    min_removed: int = 0,
) -> DeduplicationReport:
    """Deduplicate a list of changelog diffs, optionally filtering by removed count."""
    entries: List[DeduplicatedDiff] = []
    for diff in diffs:
        entry = deduplicate_diff(diff)
        if entry.removed_count >= min_removed:
            entries.append(entry)
    return DeduplicationReport(entries=entries)
