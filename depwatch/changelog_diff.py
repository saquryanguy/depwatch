"""Utilities for diffing changelog sections between two package versions."""

from dataclasses import dataclass, field
from typing import List, Optional

from depwatch.version_parser import extract_sections_between
from depwatch.cached_fetcher import cached_get_changelog


@dataclass
class ChangelogDiff:
    """Holds the raw changelog lines between two versions of a package."""

    package: str
    old_version: str
    new_version: str
    lines: List[str] = field(default_factory=list)
    error: Optional[str] = None

    @property
    def is_empty(self) -> bool:
        return not self.lines

    @property
    def found(self) -> bool:
        return self.error is None


def fetch_changelog_diff(
    package: str,
    old_version: str,
    new_version: str,
) -> ChangelogDiff:
    """Fetch and slice the changelog between old_version and new_version.

    Returns a ChangelogDiff with the relevant lines, or an error message
    if the changelog could not be retrieved or parsed.
    """
    changelog = cached_get_changelog(package)
    if changelog is None:
        return ChangelogDiff(
            package=package,
            old_version=old_version,
            new_version=new_version,
            error=f"No changelog found for {package}",
        )

    lines = extract_sections_between(changelog, old_version, new_version)
    return ChangelogDiff(
        package=package,
        old_version=old_version,
        new_version=new_version,
        lines=lines,
    )


def fetch_changelog_diffs(
    upgrades: dict,
) -> List[ChangelogDiff]:
    """Fetch changelog diffs for multiple package upgrades.

    Args:
        upgrades: dict mapping package name -> (old_version, new_version)

    Returns:
        List of ChangelogDiff instances.
    """
    results = []
    for package, (old_ver, new_ver) in upgrades.items():
        diff = fetch_changelog_diff(package, old_ver, new_ver)
        results.append(diff)
    return results
