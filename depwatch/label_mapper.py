"""Maps severity levels and categories to GitHub PR label names."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from depwatch.severity_classifier import Severity


# Default label mappings for severity levels
_DEFAULT_SEVERITY_LABELS: Dict[str, str] = {
    Severity.CRITICAL.value: "depwatch: critical",
    Severity.HIGH.value: "depwatch: high",
    Severity.MEDIUM.value: "depwatch: medium",
    Severity.LOW.value: "depwatch: low",
    Severity.SAFE.value: "depwatch: safe",
}

# Default label mappings for changelog categories
_DEFAULT_CATEGORY_LABELS: Dict[str, str] = {
    "security": "depwatch: security",
    "api": "depwatch: api-change",
    "deprecation": "depwatch: deprecation",
    "performance": "depwatch: performance",
}


@dataclass
class LabelSet:
    severity_labels: List[str] = field(default_factory=list)
    category_labels: List[str] = field(default_factory=list)

    @property
    def all_labels(self) -> List[str]:
        seen = set()
        result = []
        for label in self.severity_labels + self.category_labels:
            if label not in seen:
                seen.add(label)
                result.append(label)
        return result


def severity_to_label(
    severity: Severity,
    mapping: Optional[Dict[str, str]] = None,
) -> Optional[str]:
    """Return the GitHub label string for a given Severity enum value."""
    effective = mapping if mapping is not None else _DEFAULT_SEVERITY_LABELS
    return effective.get(severity.value)


def categories_to_labels(
    categories: List[str],
    mapping: Optional[Dict[str, str]] = None,
) -> List[str]:
    """Return label strings for a list of category names."""
    effective = mapping if mapping is not None else _DEFAULT_CATEGORY_LABELS
    return [effective[cat] for cat in categories if cat in effective]


def build_label_set(
    severity: Severity,
    categories: Optional[List[str]] = None,
    severity_mapping: Optional[Dict[str, str]] = None,
    category_mapping: Optional[Dict[str, str]] = None,
) -> LabelSet:
    """Build a LabelSet from a severity level and optional categories."""
    sev_label = severity_to_label(severity, severity_mapping)
    sev_labels = [sev_label] if sev_label else []
    cat_labels = categories_to_labels(categories or [], category_mapping)
    return LabelSet(severity_labels=sev_labels, category_labels=cat_labels)
