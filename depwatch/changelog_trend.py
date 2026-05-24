"""Tracks and analyzes risk trends across multiple pipeline runs."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from depwatch.severity import Severity
from depwatch.changelog_diff_scorer import DiffScoreEntry


@dataclass
class TrendPoint:
    run_id: str
    package: str
    score: float
    risk_label: str


@dataclass
class PackageTrend:
    package: str
    points: List[TrendPoint] = field(default_factory=list)

    @property
    def latest_score(self) -> float:
        return self.points[-1].score if self.points else 0.0

    @property
    def previous_score(self) -> float:
        return self.points[-2].score if len(self.points) >= 2 else 0.0

    @property
    def delta(self) -> float:
        return self.latest_score - self.previous_score

    @property
    def is_worsening(self) -> bool:
        return self.delta > 0

    @property
    def is_improving(self) -> bool:
        return self.delta < 0


@dataclass
class TrendReport:
    trends: List[PackageTrend] = field(default_factory=list)

    @property
    def worsening(self) -> List[PackageTrend]:
        return [t for t in self.trends if t.is_worsening]

    @property
    def improving(self) -> List[PackageTrend]:
        return [t for t in self.trends if t.is_improving]


def build_trend_report(
    history: List[tuple[str, List[DiffScoreEntry]]],
) -> TrendReport:
    """Build a trend report from ordered (run_id, entries) history."""
    package_map: dict[str, PackageTrend] = {}

    for run_id, entries in history:
        for entry in entries:
            pkg = entry.package
            if pkg not in package_map:
                package_map[pkg] = PackageTrend(package=pkg)
            package_map[pkg].points.append(
                TrendPoint(
                    run_id=run_id,
                    package=pkg,
                    score=entry.score,
                    risk_label=entry.risk_label,
                )
            )

    return TrendReport(trends=list(package_map.values()))


def format_trend_report(report: TrendReport) -> str:
    """Format trend report as a markdown summary."""
    lines = ["## Changelog Risk Trend\n"]
    if not report.trends:
        lines.append("_No trend data available._")
        return "\n".join(lines)

    for trend in sorted(report.trends, key=lambda t: -abs(t.delta)):
        arrow = "↑" if trend.is_worsening else ("↓" if trend.is_improving else "→")
        lines.append(
            f"- **{trend.package}**: {trend.previous_score:.1f} → "
            f"{trend.latest_score:.1f} {arrow} (Δ {trend.delta:+.1f})"
        )
    return "\n".join(lines)
