"""Tests for version_parser module."""

import pytest
from depwatch.version_parser import parse_version_sections, extract_sections_between


SAMPLE_CHANGELOG = """
## 2.1.0
### Added
- New feature X

## 2.0.0
### Breaking
- Removed old API

## 1.9.0
### Fixed
- Bug fix Y
"""


def test_parse_version_sections_count():
    sections = parse_version_sections(SAMPLE_CHANGELOG)
    assert len(sections) == 3


def test_parse_version_sections_versions():
    sections = parse_version_sections(SAMPLE_CHANGELOG)
    versions = [v for v, _ in sections]
    assert versions == ["2.1.0", "2.0.0", "1.9.0"]


def test_parse_version_sections_content():
    sections = parse_version_sections(SAMPLE_CHANGELOG)
    _, text = sections[1]
    assert "Removed old API" in text


def test_extract_sections_between_basic():
    result = extract_sections_between(SAMPLE_CHANGELOG, "1.9.0", "2.1.0")
    assert result is not None
    assert "New feature X" in result
    assert "Removed old API" in result
    assert "Bug fix Y" not in result


def test_extract_sections_between_no_match():
    result = extract_sections_between(SAMPLE_CHANGELOG, "2.1.0", "2.1.0")
    assert result is None


def test_extract_sections_between_empty_changelog():
    result = extract_sections_between("", "1.0.0", "2.0.0")
    assert result is None


def test_extract_sections_single_version():
    result = extract_sections_between(SAMPLE_CHANGELOG, "1.9.0", "2.0.0")
    assert result is not None
    assert "Removed old API" in result
    assert "New feature X" not in result
