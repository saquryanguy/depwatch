"""Validates changelog content for structure and completeness."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class ValidationResult:
    package: str
    is_valid: bool
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

    @property
    def has_warnings(self) -> bool:
        return len(self.warnings) > 0

    @property
    def has_errors(self) -> bool:
        return len(self.errors) > 0


def _check_has_version_headers(lines: List[str]) -> Optional[str]:
    """Return error message if no version headers are found."""
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("#") or stripped.startswith("["):
            return None
    return "No version headers detected in changelog"


def _check_min_length(lines: List[str], min_lines: int = 3) -> Optional[str]:
    non_empty = [l for l in lines if l.strip()]
    if len(non_empty) < min_lines:
        return f"Changelog too short ({len(non_empty)} non-empty lines, expected >= {min_lines})"
    return None


def _check_encoding(raw: str) -> Optional[str]:
    try:
        raw.encode("utf-8")
        return None
    except UnicodeEncodeError as exc:
        return f"Encoding error in changelog: {exc}"


def validate_changelog(
    package: str,
    content: Optional[str],
    min_lines: int = 3,
) -> ValidationResult:
    """Validate changelog content and return a ValidationResult."""
    if not content:
        return ValidationResult(
            package=package,
            is_valid=False,
            errors=["Changelog content is empty or unavailable"],
        )

    warnings: List[str] = []
    errors: List[str] = []

    enc_err = _check_encoding(content)
    if enc_err:
        errors.append(enc_err)

    lines = content.splitlines()

    length_err = _check_min_length(lines, min_lines)
    if length_err:
        warnings.append(length_err)

    header_err = _check_has_version_headers(lines)
    if header_err:
        warnings.append(header_err)

    return ValidationResult(
        package=package,
        is_valid=len(errors) == 0,
        warnings=warnings,
        errors=errors,
    )


def validate_changelogs(
    changelogs: dict,
    min_lines: int = 3,
) -> List[ValidationResult]:
    """Validate multiple changelogs given as {package: content} mapping."""
    return [
        validate_changelog(pkg, content, min_lines)
        for pkg, content in changelogs.items()
    ]
