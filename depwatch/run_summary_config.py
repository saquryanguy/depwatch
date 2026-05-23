"""Configuration for run summary output and behaviour."""

import os
from dataclasses import dataclass
from typing import Literal

OutputFormat = Literal["markdown", "plain"]


@dataclass
class RunSummaryConfig:
    """Controls how the run summary is rendered and where it goes."""

    output_format: OutputFormat = "plain"
    """Render format for the summary (plain text or markdown)."""

    fail_on_breaking: bool = True
    """Exit with a non-zero code when breaking changes are detected."""

    print_summary: bool = True
    """Whether to print the summary to stdout."""


def config_from_env() -> RunSummaryConfig:
    """Read RunSummaryConfig from environment variables.

    Environment variables:
        DEPWATCH_SUMMARY_FORMAT   – "plain" (default) or "markdown"
        DEPWATCH_FAIL_ON_BREAKING – "true" (default) or "false"
        DEPWATCH_PRINT_SUMMARY    – "true" (default) or "false"
    """
    fmt_raw = os.environ.get("DEPWATCH_SUMMARY_FORMAT", "plain").strip().lower()
    output_format: OutputFormat = "markdown" if fmt_raw == "markdown" else "plain"

    fail_on_breaking = os.environ.get("DEPWATCH_FAIL_ON_BREAKING", "true").strip().lower() != "false"
    print_summary = os.environ.get("DEPWATCH_PRINT_SUMMARY", "true").strip().lower() != "false"

    return RunSummaryConfig(
        output_format=output_format,
        fail_on_breaking=fail_on_breaking,
        print_summary=print_summary,
    )


def config_from_dict(data: dict) -> RunSummaryConfig:
    """Build a RunSummaryConfig from a plain dictionary (e.g. parsed YAML).

    Unknown keys are silently ignored.
    """
    fmt_raw = str(data.get("output_format", "plain")).strip().lower()
    output_format: OutputFormat = "markdown" if fmt_raw == "markdown" else "plain"

    fail_on_breaking = bool(data.get("fail_on_breaking", True))
    print_summary = bool(data.get("print_summary", True))

    return RunSummaryConfig(
        output_format=output_format,
        fail_on_breaking=fail_on_breaking,
        print_summary=print_summary,
    )
