"""Tests for changelog_trend and trend_config modules."""
import pytest

from depwatch.changelog_trend import (
    TrendPoint,
    PackageTrend,
    TrendReport,
    build_trend_report,
    format_trend_report,
)
from depwatch.trend_config import TrendConfig, config_from_dict, config_from_env


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

class _FakeEntry:
    """Minimal stand-in for DiffScoreEntry."""
    def __init__(self, package: str, score: float, risk_label: str = "low"):
        self.package = package
        self.score = score
        self.risk_label = risk_label


def _history(*runs):
    """Build history list: each run is (run_id, [(pkg, score), ...])."""
    result = []
    for run_id, pkgs in runs:
        entries = [_FakeEntry(pkg, score) for pkg, score in pkgs]
        result.append((run_id, entries))
    return result


# ---------------------------------------------------------------------------
# PackageTrend
# ---------------------------------------------------------------------------

def test_package_trend_latest_score_empty():
    t = PackageTrend(package="requests")
    assert t.latest_score == 0.0


def test_package_trend_delta_single_point():
    t = PackageTrend(package="requests", points=[TrendPoint("r1", "requests", 5.0, "low")])
    assert t.delta == 5.0
    assert t.previous_score == 0.0


def test_package_trend_is_worsening():
    points = [
        TrendPoint("r1", "pkg", 2.0, "low"),
        TrendPoint("r2", "pkg", 7.0, "high"),
    ]
    t = PackageTrend(package="pkg", points=points)
    assert t.is_worsening is True
    assert t.is_improving is False


def test_package_trend_is_improving():
    points = [
        TrendPoint("r1", "pkg", 8.0, "high"),
        TrendPoint("r2", "pkg", 3.0, "low"),
    ]
    t = PackageTrend(package="pkg", points=points)
    assert t.is_improving is True
    assert t.is_worsening is False


# ---------------------------------------------------------------------------
# build_trend_report
# ---------------------------------------------------------------------------

def test_build_trend_report_empty_history():
    report = build_trend_report([])
    assert isinstance(report, TrendReport)
    assert report.trends == []


def test_build_trend_report_single_run():
    history = _history(("run1", [("requests", 3.0), ("flask", 0.0)]))
    report = build_trend_report(history)
    assert len(report.trends) == 2
    packages = {t.package for t in report.trends}
    assert "requests" in packages
    assert "flask" in packages


def test_build_trend_report_accumulates_points():
    history = _history(
        ("run1", [("requests", 2.0)]),
        ("run2", [("requests", 5.0)]),
    )
    report = build_trend_report(history)
    assert len(report.trends) == 1
    assert len(report.trends[0].points) == 2


def test_build_trend_report_worsening_list():
    history = _history(
        ("run1", [("requests", 1.0)]),
        ("run2", [("requests", 9.0)]),
    )
    report = build_trend_report(history)
    assert len(report.worsening) == 1
    assert report.worsening[0].package == "requests"


def test_build_trend_report_improving_list():
    history = _history(
        ("run1", [("flask", 8.0)]),
        ("run2", [("flask", 1.0)]),
    )
    report = build_trend_report(history)
    assert len(report.improving) == 1


# ---------------------------------------------------------------------------
# format_trend_report
# ---------------------------------------------------------------------------

def test_format_trend_report_empty():
    result = format_trend_report(TrendReport())
    assert "No trend data" in result


def test_format_trend_report_contains_package():
    history = _history(
        ("r1", [("requests", 2.0)]),
        ("r2", [("requests", 6.0)]),
    )
    result = format_trend_report(build_trend_report(history))
    assert "requests" in result
    assert "↑" in result


# ---------------------------------------------------------------------------
# TrendConfig / config_from_dict
# ---------------------------------------------------------------------------

def test_config_from_dict_defaults():
    cfg = config_from_dict({})
    assert cfg.enabled is True
    assert cfg.max_history == 10
    assert cfg.min_delta_to_report == 0.0
    assert cfg.include_improving is True


def test_config_from_dict_sets_enabled_false():
    cfg = config_from_dict({"enabled": "false"})
    assert cfg.enabled is False


def test_config_from_dict_sets_max_history():
    cfg = config_from_dict({"max_history": 5})
    assert cfg.max_history == 5


def test_config_from_dict_invalid_max_history_falls_back():
    cfg = config_from_dict({"max_history": "bad"})
    assert cfg.max_history == 10


def test_config_from_dict_sets_min_delta():
    cfg = config_from_dict({"min_delta_to_report": 2.5})
    assert cfg.min_delta_to_report == 2.5


def test_config_from_dict_sets_include_improving_false():
    cfg = config_from_dict({"include_improving": "false"})
    assert cfg.include_improving is False


def test_config_from_env_defaults(monkeypatch):
    for key in [
        "DEPWATCH_TREND_ENABLED",
        "DEPWATCH_TREND_MAX_HISTORY",
        "DEPWATCH_TREND_MIN_DELTA",
        "DEPWATCH_TREND_INCLUDE_IMPROVING",
    ]:
        monkeypatch.delenv(key, raising=False)
    cfg = config_from_env()
    assert cfg.enabled is True
    assert cfg.max_history == 10


def test_config_from_env_sets_values(monkeypatch):
    monkeypatch.setenv("DEPWATCH_TREND_ENABLED", "false")
    monkeypatch.setenv("DEPWATCH_TREND_MAX_HISTORY", "3")
    monkeypatch.setenv("DEPWATCH_TREND_MIN_DELTA", "1.5")
    cfg = config_from_env()
    assert cfg.enabled is False
    assert cfg.max_history == 3
    assert cfg.min_delta_to_report == 1.5
