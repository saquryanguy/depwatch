"""Analyzes changelog sections to identify breaking changes between versions."""

import re
from typing import List

BREAKING_PATTERNS = [
    r"\bbreaking\b",
    r"\bremoved?\b",
    r"\bdeprecated?\b",
    r"\bincompatible\b",
    r"\bmigration\b",
    r"\brenamed?\b",
    r"\bdropped?\b",
    r"!\s*important",
]

COMPILED_PATTERNS = [re.compile(p, re.IGNORECASE) for p in BREAKING_PATTERNS]


def is_breaking_line(line: str) -> bool:
    """Return True if the line likely describes a breaking change."""
    return any(pat.search(line) for pat in COMPILED_PATTERNS)


def extract_breaking_changes(sections: dict[str, str]) -> dict[str, List[str]]:
    """
    Given a dict of {version: changelog_text}, return a dict of
    {version: [breaking_change_lines]} for versions that contain breaking changes.
    """
    result: dict[str, List[str]] = {}
    for version, text in sections.items():
        breaking = []
        for line in text.splitlines():
            stripped = line.strip()
            if stripped and is_breaking_line(stripped):
                breaking.append(stripped)
        if breaking:
            result[version] = breaking
    return result


def summarize_breaking_changes(breaking: dict[str, List[str]]) -> str:
    """Format breaking changes into a human-readable markdown summary."""
    if not breaking:
        return "No breaking changes detected."

    lines = ["### ⚠️ Breaking Changes Detected\n"]
    for version, changes in breaking.items():
        lines.append(f"**{version}**")
        for change in changes:
            lines.append(f"- {change}")
        lines.append("")
    return "\n".join(lines).strip()
