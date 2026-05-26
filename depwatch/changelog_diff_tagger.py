"""Tag changelog diffs with semantic labels based on content and severity."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from depwatch.changelog_diff import ChangelogDiff
from depwatch.severity_classifier import Severity, classify_changes, highest_severity


@dataclass
class TaggedDiff:
    diff: ChangelogDiff
    tags: List[str] = field(default_factory=list)
    severity: Severity = Severity.SAFE

    @property
    def package(self) -> str:
        return self.diff.package

    @property
    def is_tagged(self) -> bool:
        return len(self.tags) > 0


@dataclass
class TaggerReport:
    entries: List[TaggedDiff] = field(default_factory=list)

    @property
    def total(self) -> int:
        return len(self.entries)

    @property
    def tagged_count(self) -> int:
        return sum(1 for e in self.entries if e.is_tagged)


_SEVERITY_TAG_MAP = {
    Severity.CRITICAL: "breaking",
    Severity.HIGH: "high-risk",
    Severity.MEDIUM: "moderate-risk",
    Severity.LOW: "low-risk",
    Severity.SAFE: "safe",
}

_KEYWORD_TAGS = [
    ("security", ["cve", "vulnerability", "security fix", "exploit"]),
    ("deprecation", ["deprecated", "deprecation", "will be removed"]),
    ("api-change", ["breaking change", "removed", "renamed", "signature changed"]),
    ("performance", ["performance", "speed", "faster", "slower", "latency"]),
]


def _keyword_tags_for_lines(lines: List[str]) -> List[str]:
    joined = "\n".join(lines).lower()
    found = []
    for tag, keywords in _KEYWORD_TAGS:
        if any(kw in joined for kw in keywords):
            found.append(tag)
    return found


def tag_diff(diff: ChangelogDiff, extra_tags: Optional[List[str]] = None) -> TaggedDiff:
    lines = diff.lines if diff.lines else []
    classified = classify_changes(lines)
    sev = highest_severity(classified)
    tags: List[str] = []
    sev_tag = _SEVERITY_TAG_MAP.get(sev)
    if sev_tag:
        tags.append(sev_tag)
    tags.extend(_keyword_tags_for_lines(lines))
    if extra_tags:
        tags.extend(extra_tags)
    return TaggedDiff(diff=diff, tags=list(dict.fromkeys(tags)), severity=sev)


def tag_diffs(
    diffs: List[ChangelogDiff], extra_tags: Optional[List[str]] = None
) -> TaggerReport:
    entries = [tag_diff(d, extra_tags=extra_tags) for d in diffs]
    return TaggerReport(entries=entries)
