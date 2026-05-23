"""Tests for depwatch.output_formatter."""

from __future__ import annotations

import pytest

from depwatch.output_formatter import (
    PackageReport,
    format_markdown_report,
    format_plain_text_report,
    format_table_row,
)


@pytest.fixture
def safe_report() -> PackageReport:
    return PackageReport(
        package="requests",
        old_version="2.28.0",
        new_version="2.29.0",
        breaking_changes=[],
        summary="",
    )


@pytest.fixture
def breaking_report() -> PackageReport:
    return PackageReport(
        package="django",
        old_version="4.1.0",
        new_version="5.0.0",
        breaking_changes=["Removed support for Python 3.8", "Dropped `ugettext` alias"],
        summary="- Removed support for Python 3.8\n- Dropped `ugettext` alias",
    )


def test_format_table_row_safe(safe_report):
    row = format_table_row(safe_report)
    assert "`requests`" in row
    assert "2.28.0" in row
    assert "2.29.0" in row
    assert "✅ Safe" in row
    assert "| 0 |" in row


def test_format_table_row_breaking(breaking_report):
    row = format_table_row(breaking_report)
    assert "`django`" in row
    assert "⚠️ Breaking" in row
    assert "| 2 |" in row


def test_format_markdown_report_empty():
    result = format_markdown_report([])
    assert "No dependency changes detected" in result


def test_format_markdown_report_contains_table_header(safe_report):
    result = format_markdown_report([safe_report])
    assert "| Package |" in result
    assert "| Version |" in result


def test_format_markdown_report_includes_package(safe_report):
    result = format_markdown_report([safe_report])
    assert "`requests`" in result


def test_format_markdown_report_breaking_details_section(breaking_report):
    result = format_markdown_report([breaking_report])
    assert "Breaking Change Details" in result
    assert "Removed support for Python 3.8" in result


def test_format_markdown_report_no_details_when_all_safe(safe_report):
    result = format_markdown_report([safe_report])
    assert "Breaking Change Details" not in result


def test_format_markdown_report_footer(safe_report):
    result = format_markdown_report([safe_report])
    assert "DepWatch" in result
    assert "---" in result


def test_format_plain_text_empty():
    result = format_plain_text_report([])
    assert "No dependency changes detected" in result


def test_format_plain_text_ok_label(safe_report):
    result = format_plain_text_report([safe_report])
    assert "[OK]" in result
    assert "requests" in result


def test_format_plain_text_breaking_label(breaking_report):
    result = format_plain_text_report([breaking_report])
    assert "[BREAKING]" in result
    assert "django" in result


def test_format_plain_text_lists_changes(breaking_report):
    result = format_plain_text_report([breaking_report])
    assert "Removed support for Python 3.8" in result
    assert "Dropped `ugettext` alias" in result
