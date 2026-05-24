"""Tests for depwatch.label_mapper."""

import pytest

from depwatch.severity_classifier import Severity
from depwatch.label_mapper import (
    LabelSet,
    severity_to_label,
    categories_to_labels,
    build_label_set,
)


# ---------------------------------------------------------------------------
# severity_to_label
# ---------------------------------------------------------------------------

def test_severity_to_label_critical():
    assert severity_to_label(Severity.CRITICAL) == "depwatch: critical"


def test_severity_to_label_safe():
    assert severity_to_label(Severity.SAFE) == "depwatch: safe"


def test_severity_to_label_custom_mapping():
    custom = {Severity.HIGH.value: "priority: high"}
    assert severity_to_label(Severity.HIGH, mapping=custom) == "priority: high"


def test_severity_to_label_missing_in_custom_returns_none():
    assert severity_to_label(Severity.MEDIUM, mapping={}) is None


# ---------------------------------------------------------------------------
# categories_to_labels
# ---------------------------------------------------------------------------

def test_categories_to_labels_known():
    labels = categories_to_labels(["security", "api"])
    assert "depwatch: security" in labels
    assert "depwatch: api-change" in labels


def test_categories_to_labels_unknown_skipped():
    labels = categories_to_labels(["unknown_category"])
    assert labels == []


def test_categories_to_labels_empty():
    assert categories_to_labels([]) == []


def test_categories_to_labels_custom_mapping():
    custom = {"security": "sec-alert"}
    labels = categories_to_labels(["security"], mapping=custom)
    assert labels == ["sec-alert"]


# ---------------------------------------------------------------------------
# LabelSet
# ---------------------------------------------------------------------------

def test_label_set_all_labels_combines():
    ls = LabelSet(severity_labels=["depwatch: critical"], category_labels=["depwatch: security"])
    assert ls.all_labels == ["depwatch: critical", "depwatch: security"]


def test_label_set_all_labels_deduplicates():
    ls = LabelSet(
        severity_labels=["depwatch: high"],
        category_labels=["depwatch: high", "depwatch: security"],
    )
    assert ls.all_labels.count("depwatch: high") == 1


def test_label_set_all_labels_empty():
    ls = LabelSet()
    assert ls.all_labels == []


# ---------------------------------------------------------------------------
# build_label_set
# ---------------------------------------------------------------------------

def test_build_label_set_returns_label_set():
    ls = build_label_set(Severity.HIGH)
    assert isinstance(ls, LabelSet)


def test_build_label_set_severity_label_present():
    ls = build_label_set(Severity.CRITICAL)
    assert "depwatch: critical" in ls.severity_labels


def test_build_label_set_with_categories():
    ls = build_label_set(Severity.HIGH, categories=["security", "deprecation"])
    assert "depwatch: security" in ls.category_labels
    assert "depwatch: deprecation" in ls.category_labels


def test_build_label_set_no_categories_empty_cat_labels():
    ls = build_label_set(Severity.MEDIUM)
    assert ls.category_labels == []


def test_build_label_set_all_labels_contains_both():
    ls = build_label_set(Severity.HIGH, categories=["api"])
    all_labels = ls.all_labels
    assert "depwatch: high" in all_labels
    assert "depwatch: api-change" in all_labels
