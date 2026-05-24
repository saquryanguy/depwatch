"""Scores changelog diffs by assigning a numeric risk score based on severity and content."""

from dataclasses import dataclass, field
from typing import List, Optional

from depwatch.severity_classifier import Severity, classify_changes
from depwatch.changelog_diff import ChangelogDiff

# Weight multipliers per severity level
_SEVERITY_WEIGHTS: dict = {
    Severity.CRITICAL: 10,
    Severity.HIGH: 5,
    Severity.MEDIUM: 2,
    Severity.LOW: 1,
    Severity.SAFE: 0,
}


@dataclass
class ChangelogScore:
    package: str
    old_version: str
    new_version: str
    score: int
    line_count: int
    severity_counts: dict = field(default_factory=dict)
    risk_label: str = "safe"


def _risk_label(score: int) -> str:
    """Map a numeric score to a human-readable risk label."""
    if score >= 30:
        return "critical"
    if score >= 15:
        return "high"
    if score >= 5:
        return "medium"
    if score > 0:
        return "low"
    return "safe"


def score_changelog_diff(diff: ChangelogDiff) -> ChangelogScore:
    """Compute a numeric risk score for a single ChangelogDiff."""
    lines = diff.lines if diff.lines else []
    severities = classify_changes(lines)

    counts: dict = {}
    total = 0
    for sev in severities:
        counts[sev] = counts.get(sev, 0) + 1
        total += _SEVERITY_WEIGHTS.get(sev, 0)

    return ChangelogScore(
        package=diff.package,
        old_version=diff.old_version,
        new_version=diff.new_version,
        score=total,
        line_count=len(lines),
        severity_counts={s.value: c for s, c in counts.items()},
        risk_label=_risk_label(total),
    )


def score_changelog_diffs(diffs: List[ChangelogDiff]) -> List[ChangelogScore]:
    """Score a list of ChangelogDiff objects, sorted by descending score."""
    scores = [score_changelog_diff(d) for d in diffs]
    return sorted(scores, key=lambda s: s.score, reverse=True)


def top_risk_packages(scores: List[ChangelogScore], n: int = 5) -> List[ChangelogScore]:
    """Return the top-n highest risk packages from a scored list."""
    return scores[:n]
