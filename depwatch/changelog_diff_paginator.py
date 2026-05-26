"""Pagination support for large changelog diff result sets."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from depwatch.changelog_diff import ChangelogDiff


@dataclass
class PaginatedDiffResult:
    """A single page of changelog diffs."""

    items: List[ChangelogDiff]
    page: int
    page_size: int
    total: int

    @property
    def total_pages(self) -> int:
        if self.page_size <= 0:
            return 0
        return max(1, (self.total + self.page_size - 1) // self.page_size)

    @property
    def has_next(self) -> bool:
        return self.page < self.total_pages

    @property
    def has_previous(self) -> bool:
        return self.page > 1


@dataclass
class PaginatorConfig:
    page_size: int = 10
    page: int = 1


def paginate_diffs(
    diffs: List[ChangelogDiff],
    config: Optional[PaginatorConfig] = None,
) -> PaginatedDiffResult:
    """Return a single page of diffs according to *config*.

    Pages are 1-indexed.  If *page* is out of range the closest valid page
    is returned (first or last).
    """
    if config is None:
        config = PaginatorConfig()

    page_size = max(1, config.page_size)
    total = len(diffs)
    total_pages = max(1, (total + page_size - 1) // page_size)
    page = max(1, min(config.page, total_pages))

    start = (page - 1) * page_size
    end = start + page_size
    items = diffs[start:end]

    return PaginatedDiffResult(
        items=items,
        page=page,
        page_size=page_size,
        total=total,
    )


def iter_pages(
    diffs: List[ChangelogDiff],
    page_size: int = 10,
):
    """Yield successive :class:`PaginatedDiffResult` pages for *diffs*."""
    config = PaginatorConfig(page_size=page_size, page=1)
    result = paginate_diffs(diffs, config)
    yield result
    while result.has_next:
        config = PaginatorConfig(page_size=page_size, page=result.page + 1)
        result = paginate_diffs(diffs, config)
        yield result
