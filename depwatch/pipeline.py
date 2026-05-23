"""High-level pipeline that wires together dependency diffing, changelog
fetching, severity classification, and report building."""

from typing import List, Optional

from depwatch.dependency_reader import diff_dependencies
from depwatch.changelog_diff import fetch_changelog_diffs, ChangelogDiff
from depwatch.severity_report import SeverityReport, build_severity_report
from depwatch.filter_engine import FilterCriteria
from depwatch.filtered_report import build_filtered_report


def _upgrades_from_diff(old_deps: dict, new_deps: dict) -> dict:
    """Return a dict of packages that were upgraded: name -> (old, new)."""
    added, removed, changed = diff_dependencies(old_deps, new_deps)
    upgrades = {}
    for pkg, (old_ver, new_ver) in changed.items():
        # Only track actual upgrades (new > old), not downgrades
        upgrades[pkg] = (old_ver, new_ver)
    return upgrades


def run_pipeline(
    old_deps: dict,
    new_deps: dict,
    criteria: Optional[FilterCriteria] = None,
) -> List[SeverityReport]:
    """Run the full depwatch pipeline.

    1. Diff old vs new dependency sets to find upgrades.
    2. Fetch changelog sections for each upgrade.
    3. Build a SeverityReport for each package.
    4. Optionally filter reports by criteria.

    Args:
        old_deps: dict of package -> version before the PR.
        new_deps: dict of package -> version after the PR.
        criteria: optional FilterCriteria to exclude low-signal reports.

    Returns:
        List of SeverityReport instances (filtered if criteria provided).
    """
    upgrades = _upgrades_from_diff(old_deps, new_deps)
    if not upgrades:
        return []

    diffs: List[ChangelogDiff] = fetch_changelog_diffs(upgrades)

    reports: List[SeverityReport] = []
    for diff in diffs:
        report = build_severity_report(
            package=diff.package,
            old_version=diff.old_version,
            new_version=diff.new_version,
            lines=diff.lines,
        )
        if criteria is not None:
            filtered = build_filtered_report(report, criteria)
            if filtered is not None:
                reports.append(filtered)
        else:
            reports.append(report)

    return reports
