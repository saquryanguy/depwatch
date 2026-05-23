"""Retry logic with exponential backoff for network requests."""

import time
import logging
from typing import Callable, TypeVar, Optional, Tuple, Type

logger = logging.getLogger(__name__)

T = TypeVar("T")

DEFAULT_RETRIES = 3
DEFAULT_BACKOFF_BASE = 2.0
DEFAULT_BACKOFF_MAX = 30.0


def with_retry(
    fn: Callable[[], T],
    retries: int = DEFAULT_RETRIES,
    backoff_base: float = DEFAULT_BACKOFF_BASE,
    backoff_max: float = DEFAULT_BACKOFF_MAX,
    retriable_exceptions: Tuple[Type[Exception], ...] = (Exception,),
    sleep_fn: Optional[Callable[[float], None]] = None,
) -> T:
    """Call *fn* up to *retries* times, sleeping with exponential backoff on failure.

    Args:
        fn: Zero-argument callable to execute.
        retries: Maximum number of attempts (including the first).
        backoff_base: Multiplier for exponential backoff (seconds).
        backoff_max: Upper bound on sleep duration.
        retriable_exceptions: Only retry on these exception types.
        sleep_fn: Injectable sleep function (defaults to time.sleep).

    Returns:
        The return value of *fn* on success.

    Raises:
        The last exception raised by *fn* after all retries are exhausted.
    """
    _sleep = sleep_fn if sleep_fn is not None else time.sleep
    last_exc: Optional[Exception] = None

    for attempt in range(1, retries + 1):
        try:
            return fn()
        except retriable_exceptions as exc:  # type: ignore[misc]
            last_exc = exc
            if attempt == retries:
                logger.warning(
                    "All %d attempts failed for %s: %s", retries, getattr(fn, "__name__", fn), exc
                )
                break
            delay = min(backoff_base ** (attempt - 1), backoff_max)
            logger.debug(
                "Attempt %d/%d failed (%s). Retrying in %.1fs.",
                attempt,
                retries,
                exc,
                delay,
            )
            _sleep(delay)

    raise last_exc  # type: ignore[misc]
