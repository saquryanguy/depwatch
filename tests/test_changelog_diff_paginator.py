"""Tests for depwatch.changelog_diff_paginator."""
from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from depwatch.changelog_diff_paginator import (
    PaginatedDiffResult,
    PaginatorConfig,
    iter_pages,
    paginate_diffs,
)


def _make_diff(package: str):
    diff = MagicMock()
    diff.package = package
    return diff


DIFFS = [_make_diff(f"pkg{i}") for i in range(25)]


# ---------------------------------------------------------------------------
# PaginatedDiffResult properties
# ---------------------------------------------------------------------------

def test_total_pages_exact_multiple():
    r = PaginatedDiffResult(items=[], page=1, page_size=5, total=10)
    assert r.total_pages == 2


def test_total_pages_remainder():
    r = PaginatedDiffResult(items=[], page=1, page_size=5, total=11)
    assert r.total_pages == 3


def test_total_pages_zero_total():
    r = PaginatedDiffResult(items=[], page=1, page_size=10, total=0)
    assert r.total_pages == 1


def test_has_next_true():
    r = PaginatedDiffResult(items=[], page=1, page_size=10, total=25)
    assert r.has_next is True


def test_has_next_false_on_last_page():
    r = PaginatedDiffResult(items=[], page=3, page_size=10, total=25)
    assert r.has_next is False


def test_has_previous_false_on_first_page():
    r = PaginatedDiffResult(items=[], page=1, page_size=10, total=25)
    assert r.has_previous is False


def test_has_previous_true_on_later_page():
    r = PaginatedDiffResult(items=[], page=2, page_size=10, total=25)
    assert r.has_previous is True


# ---------------------------------------------------------------------------
# paginate_diffs
# ---------------------------------------------------------------------------

def test_paginate_diffs_first_page_count():
    result = paginate_diffs(DIFFS, PaginatorConfig(page_size=10, page=1))
    assert len(result.items) == 10


def test_paginate_diffs_last_page_partial():
    result = paginate_diffs(DIFFS, PaginatorConfig(page_size=10, page=3))
    assert len(result.items) == 5


def test_paginate_diffs_page_out_of_range_clamps_to_last():
    result = paginate_diffs(DIFFS, PaginatorConfig(page_size=10, page=999))
    assert result.page == 3


def test_paginate_diffs_page_zero_clamps_to_first():
    result = paginate_diffs(DIFFS, PaginatorConfig(page_size=10, page=0))
    assert result.page == 1


def test_paginate_diffs_total_is_full_list_length():
    result = paginate_diffs(DIFFS, PaginatorConfig(page_size=10, page=1))
    assert result.total == len(DIFFS)


def test_paginate_diffs_empty_list():
    result = paginate_diffs([], PaginatorConfig(page_size=10, page=1))
    assert result.items == []
    assert result.total == 0
    assert result.total_pages == 1


def test_paginate_diffs_default_config():
    result = paginate_diffs(DIFFS)
    assert result.page_size == 10
    assert result.page == 1


# ---------------------------------------------------------------------------
# iter_pages
# ---------------------------------------------------------------------------

def test_iter_pages_yields_all_pages():
    pages = list(iter_pages(DIFFS, page_size=10))
    assert len(pages) == 3


def test_iter_pages_covers_all_items():
    all_items = [item for page in iter_pages(DIFFS, page_size=10) for item in page.items]
    assert len(all_items) == len(DIFFS)


def test_iter_pages_empty_yields_one_page():
    pages = list(iter_pages([], page_size=10))
    assert len(pages) == 1
    assert pages[0].items == []
