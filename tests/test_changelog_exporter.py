"""Tests for depwatch.changelog_exporter."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from depwatch.changelog_exporter import ExportConfig, export_reports, export_to_file
from depwatch.severity import Severity
from depwatch.severity_report import SeverityReport
from depwatch.changelog_annotator import AnnotatedLine


def _make_report(pkg: str = "requests", sev: Severity = Severity.HIGH) -> SeverityReport:
    line = AnnotatedLine(text="Removed legacy API", severity=sev, categories=["api"])
    return SeverityReport(
        package=pkg,
        old_version="1.0.0",
        new_version="2.0.0",
        highest_severity=sev,
        annotated_lines=[line],
    )


def test_export_reports_markdown_contains_package():
    report = _make_report()
    result = export_reports([report], ExportConfig(output_format="markdown"))
    assert "requests" in result


def test_export_reports_plain_contains_package():
    report = _make_report()
    result = export_reports([report], ExportConfig(output_format="plain"))
    assert "requests" in result


def test_export_reports_json_is_valid():
    report = _make_report()
    result = export_reports([report], ExportConfig(output_format="json"))
    parsed = json.loads(result)
    assert isinstance(parsed, list)
    assert parsed[0]["package"] == "requests"


def test_export_reports_json_includes_severity():
    report = _make_report(sev=Severity.CRITICAL)
    result = export_reports([report], ExportConfig(output_format="json"))
    parsed = json.loads(result)
    assert parsed[0]["highest_severity"] == "critical"


def test_export_reports_writes_file(tmp_path):
    report = _make_report()
    out = tmp_path / "report.md"
    export_reports([report], ExportConfig(output_format="markdown", output_path=str(out)))
    assert out.exists()
    assert "requests" in out.read_text()


def test_export_to_file_creates_parent_dirs(tmp_path):
    report = _make_report()
    out = tmp_path / "sub" / "dir" / "report.json"
    export_to_file([report], str(out), fmt="json")
    assert out.exists()


def test_export_reports_empty_list_json():
    result = export_reports([], ExportConfig(output_format="json"))
    assert json.loads(result) == []


def test_export_reports_unknown_format_falls_back_to_markdown():
    report = _make_report()
    result = export_reports([report], ExportConfig(output_format="xml"))
    # Should not raise and should produce some output
    assert len(result) > 0
