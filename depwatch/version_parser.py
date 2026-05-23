"""Extracts changelog sections relevant to a version range."""

import re
from typing import List, Optional, Tuple

VERSION_HEADER_RE = re.compile(
    r"^#{1,3}\s+(?:v|version\s+)?(\d+\.\d+(?:\.\d+)?(?:[\w.-]*))",
    re.IGNORECASE | re.MULTILINE,
)


def parse_version_sections(changelog: str) -> List[Tuple[str, str]]:
    """Return list of (version, section_text) tuples from a changelog."""
    matches = list(VERSION_HEADER_RE.finditer(changelog))
    sections = []
    for i, match in enumerate(matches):
        version = match.group(1)
        start = match.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(changelog)
        section_text = changelog[start:end].strip()
        sections.append((version, section_text))
    return sections


def _version_tuple(version: str) -> Tuple:
    """Convert version string to comparable tuple."""
    return tuple(int(x) for x in re.findall(r"\d+", version)[:3])


def extract_sections_between(
    changelog: str, from_version: str, to_version: str
) -> Optional[str]:
    """
    Extract changelog sections for versions strictly greater than
    `from_version` and up to and including `to_version`.
    """
    sections = parse_version_sections(changelog)
    if not sections:
        return None

    from_t = _version_tuple(from_version)
    to_t = _version_tuple(to_version)

    relevant = [
        text
        for ver, text in sections
        if from_t < _version_tuple(ver) <= to_t
    ]

    return "\n\n".join(relevant) if relevant else None
