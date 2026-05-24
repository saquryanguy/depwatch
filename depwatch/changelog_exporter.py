"""Export changelog reports to various output formats (JSON, Markdown, plain text)."""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import List, Optional

from depwatch.severity_report import SeverityReport
from depwatch.output_formatter import format_markdown_report, format_plain_text_report


@dataclass
class ExportConfig:
    output_format: str = "markdown"  # markdown | plain | json
    output_path: Optional[str] = None  # None => return string only
    include_safe: bool = False


def _report_to_dict(report: SeverityReport) -> dict:
    return {
        "package": report.package,
        "old_version": report.old_version,
        "new_version": report.new_version,
        "highest_severity": report.highest_severity.value,
        "breaking_count": len(report.annotated_lines),
    }


def export_reports(
    reports: List[SeverityReport],
    config: ExportConfig,
) -> str:
    """Render *reports* according to *config* and optionally write to disk."""
    fmt = config.output_format.lower()

    if fmt == "json":
        payload = [_report_to_dict(r) for r in reports]
        content = json.dumps(payload, indent=2)
    elif fmt == "plain":
        content = format_plain_text_report(reports)
    else:
        content = format_markdown_report(reports)

    if config.output_path:
        path = Path(config.output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    return content


def export_to_file(reports: List[SeverityReport], path: str, fmt: str = "markdown") -> None:
    """Convenience wrapper that writes *reports* to *path* in *fmt* format."""
    cfg = ExportConfig(output_format=fmt, output_path=path)
    export_reports(reports, cfg)
