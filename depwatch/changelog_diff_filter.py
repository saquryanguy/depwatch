"""Filter changelog diffs based on score thresholds and risk criteria."""

from dataclasses import dataclass, field
from typing import List, Optional

from depwatch.changelog_diff import ChangelogDiff
from depwatch.changelog_diff_scorer import DiffScoreEntry, DiffScoreReport, build_diff_score_report
from depwatch.severity import Severity


@dataclass
class DiffFilterCriteria:
    min_score: float = 0.0
    only_risky: bool = False
    max_results: Optional[int] = None
    excluded_packages: List[str] = field(default_factory=list)


@dataclass
class FilteredDiffReport:
    criteria: DiffFilterCriteria
    included: List[DiffScoreEntry] = field(default_factory=list)
    excluded: List[DiffScoreEntry] = field(default_factory=list)

    @property
    def total_input(self) -> int:
        return len(self.included) + len(self.excluded)

    @property
    def has_risky(self) -> bool:
        return any(e.is_risky for e in self.included)


def _normalize(name: str) -> str:
    return name.strip().lower().replace("-", "_")


def filter_diff_entries(
    entries: List[DiffScoreEntry],
    criteria: DiffFilterCriteria,
) -> FilteredDiffReport:
    """Apply filter criteria to a list of scored diff entries."""
    report = FilteredDiffReport(criteria=criteria)
    excluded_set = {_normalize(p) for p in criteria.excluded_packages}

    for entry in entries:
        pkg = _normalize(entry.package)
        if pkg in excluded_set:
            report.excluded.append(entry)
            continue
        if criteria.only_risky and not entry.is_risky:
            report.excluded.append(entry)
            continue
        if entry.score < criteria.min_score:
            report.excluded.append(entry)
            continue
        report.included.append(entry)

    if criteria.max_results is not None:
        overflow = report.included[criteria.max_results:]
        report.excluded.extend(overflow)
        report.included = report.included[: criteria.max_results]

    return report


def filter_changelog_diffs(
    diffs: List[ChangelogDiff],
    criteria: DiffFilterCriteria,
) -> FilteredDiffReport:
    """Score diffs then apply filter criteria, returning a FilteredDiffReport."""
    score_report: DiffScoreReport = build_diff_score_report(diffs)
    return filter_diff_entries(score_report.entries, criteria)
