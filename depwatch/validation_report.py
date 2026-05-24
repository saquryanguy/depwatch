"""Formats ValidationResult objects into human-readable reports."""
from __future__ import annotations

from typing import List

from depwatch.changelog_validator import ValidationResult


def _status_icon(result: ValidationResult) -> str:
    if not result.is_valid:
        return "❌"
    if result.has_warnings:
        return "⚠️"
    return "✅"


def format_validation_result(result: ValidationResult) -> str:
    """Return a single-package validation summary string."""
    icon = _status_icon(result)
    lines = [f"{icon} **{result.package}**"]

    for err in result.errors:
        lines.append(f"  - 🔴 Error: {err}")
    for warn in result.warnings:
        lines.append(f"  - 🟡 Warning: {warn}")

    if result.is_valid and not result.has_warnings:
        lines.append("  - Changelog looks good.")

    return "\n".join(lines)


def format_validation_report(results: List[ValidationResult]) -> str:
    """Return a full markdown validation report for multiple packages."""
    if not results:
        return "## Changelog Validation\n\nNo packages to validate.\n"

    total = len(results)
    valid = sum(1 for r in results if r.is_valid)
    warned = sum(1 for r in results if r.is_valid and r.has_warnings)
    invalid = total - valid

    header = (
        f"## Changelog Validation\n\n"
        f"Checked **{total}** package(s): "
        f"{valid} valid, {warned} with warnings, {invalid} invalid.\n"
    )

    sections = [format_validation_result(r) for r in results]
    return header + "\n".join(sections) + "\n"


def validation_passed(results: List[ValidationResult]) -> bool:
    """Return True only if every result is valid (no errors)."""
    return all(r.is_valid for r in results)
