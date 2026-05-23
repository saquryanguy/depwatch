"""Simple rate limiter for external API calls (PyPI, GitHub)."""

import time
import threading
from collections import deque
from typing import Optional


class RateLimiter:
    """Token-bucket style rate limiter that tracks calls per window."""

    def __init__(self, max_calls: int, window_seconds: float):
        """
        Args:
            max_calls: Maximum number of calls allowed within the window.
            window_seconds: Duration of the rolling window in seconds.
        """
        self.max_calls = max_calls
        self.window_seconds = window_seconds
        self._timestamps: deque = deque()
        self._lock = threading.Lock()

    def acquire(self, block: bool = True) -> bool:
        """Acquire a rate-limit slot.

        Args:
            block: If True, sleep until a slot is available.
                   If False, return False immediately when throttled.

        Returns:
            True if the call is allowed, False if throttled and block=False.
        """
        while True:
            with self._lock:
                now = time.monotonic()
                cutoff = now - self.window_seconds
                # Evict timestamps outside the window
                while self._timestamps and self._timestamps[0] < cutoff:
                    self._timestamps.popleft()

                if len(self._timestamps) < self.max_calls:
                    self._timestamps.append(now)
                    return True

                if not block:
                    return False

                # Calculate how long to wait before the oldest slot expires
                wait_time = self._timestamps[0] - cutoff

            time.sleep(wait_time)

    def remaining(self) -> int:
        """Return the number of calls remaining in the current window."""
        with self._lock:
            now = time.monotonic()
            cutoff = now - self.window_seconds
            active = sum(1 for ts in self._timestamps if ts >= cutoff)
            return max(0, self.max_calls - active)


# Module-level default limiters
pypi_limiter: Optional[RateLimiter] = RateLimiter(max_calls=30, window_seconds=60.0)
github_limiter: Optional[RateLimiter] = RateLimiter(max_calls=20, window_seconds=60.0)
