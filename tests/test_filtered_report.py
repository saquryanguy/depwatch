"""Tests for depwatch.filtered_report."""

from depwatch.filter_engine import FilterCriteria
from depwatch.filtered_report import build_filtered_report, build_filtered_reports
from depwatch.severity_classifier import Severity

_LINES = [
    "Removed support for Python 3.7",
    "Fixed typo in docs",
    "Deprecated old_helper, use new_helper instead",
]


# ---------------------------------------------------------------------------
# build_filtered_report
# ---------------------------------------------------------------------------

def test_build_filtered_report_returns_severity_report():
    criteria = FilterCriteria()
    report = build_filtered_report("mylib", "1.0", "2.0", _LINES, criteria)
    assert report is not None
    assert report.package == "mylib"


def test_build_filtered_report_versions_preserved():
    criteria = FilterCriteria()
    report = build_filtered_report("mylib", "1.0", "2.0", _LINES, criteria)
    assert report.old_version == "1.0"
    assert report.new_version == "2.0"


def test_build_filtered_report_excluded_package_returns_none():
    criteria = FilterCriteria(packages=["other"])
    result = build_filtered_report("mylib", "1.0", "2.0", _LINES, criteria)
    assert result is None


def test_build_filtered_report_high_severity_filters_low():
    criteria = FilterCriteria(min_severity=Severity.CRITICAL)
    report = build_filtered_report("mylib", "1.0", "2.0", _LINES, criteria)
    assert report is not None
    # Only the "Removed" line should survive CRITICAL filter
    surviving = [line for line, _ in report.annotated_lines]
    assert all("Removed" in l or "Breaking" in l or "removed" in l.lower() for l in surviving)


def test_build_filtered_report_empty_lines_is_safe():
    criteria = FilterCriteria()
    report = build_filtered_report("mylib", "1.0", "2.0", [], criteria)
    assert report is not None
    assert report.is_safe is True


def test_build_filtered_report_keyword_filter():
    criteria = FilterCriteria(keywords=["Deprecated"])
    report = build_filtered_report("mylib", "1.0", "2.0", _LINES, criteria)
    assert report is not None
    surviving = [line for line, _ in report.annotated_lines]
    assert len(surviving) == 1
    assert "Deprecated" in surviving[0]


# ---------------------------------------------------------------------------
# build_filtered_reports
# ---------------------------------------------------------------------------

_PACKAGES = {
    "requests": ("2.28.0", "2.31.0", _LINES),
    "flask": ("2.0.0", "3.0.0", ["Removed deprecated app.run() shortcut"]),
    "safe-lib": ("1.0", "1.1", ["Minor performance improvements"]),
}


def test_build_filtered_reports_all_included():
    criteria = FilterCriteria()
    reports = build_filtered_reports(_PACKAGES, criteria)
    assert len(reports) == 3


def test_build_filtered_reports_package_filter():
    criteria = FilterCriteria(packages=["requests"])
    reports = build_filtered_reports(_PACKAGES, criteria)
    assert len(reports) == 1
    assert reports[0].package == "requests"


def test_build_filtered_reports_empty_packages():
    reports = build_filtered_reports({}, FilterCriteria())
    assert reports == []


def test_build_filtered_reports_preserves_order():
    criteria = FilterCriteria()
    reports = build_filtered_reports(_PACKAGES, criteria)
    names = [r.package for r in reports]
    assert names == list(_PACKAGES.keys())
