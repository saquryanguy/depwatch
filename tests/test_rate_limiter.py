"""Tests for depwatch.rate_limiter."""

import time
import threading

import pytest

from depwatch.rate_limiter import RateLimiter


def test_remaining_starts_at_max():
    rl = RateLimiter(max_calls=5, window_seconds=60.0)
    assert rl.remaining() == 5


def test_acquire_reduces_remaining():
    rl = RateLimiter(max_calls=5, window_seconds=60.0)
    rl.acquire()
    assert rl.remaining() == 4


def test_acquire_returns_true_within_limit():
    rl = RateLimiter(max_calls=3, window_seconds=60.0)
    for _ in range(3):
        assert rl.acquire() is True


def test_acquire_non_blocking_returns_false_when_exhausted():
    rl = RateLimiter(max_calls=2, window_seconds=60.0)
    assert rl.acquire(block=False) is True
    assert rl.acquire(block=False) is True
    assert rl.acquire(block=False) is False


def test_remaining_is_zero_when_exhausted():
    rl = RateLimiter(max_calls=2, window_seconds=60.0)
    rl.acquire(block=False)
    rl.acquire(block=False)
    assert rl.remaining() == 0


def test_slots_replenish_after_window(monkeypatch):
    """Simulate window expiry by manipulating monotonic time."""
    fake_time = [0.0]

    def mock_monotonic():
        return fake_time[0]

    monkeypatch.setattr(time, "monotonic", mock_monotonic)

    rl = RateLimiter(max_calls=2, window_seconds=10.0)
    assert rl.acquire(block=False) is True
    assert rl.acquire(block=False) is True
    assert rl.acquire(block=False) is False

    # Advance time past the window
    fake_time[0] = 11.0
    assert rl.acquire(block=False) is True
    assert rl.remaining() == 1


def test_thread_safety():
    """Multiple threads should not exceed max_calls."""
    max_calls = 10
    rl = RateLimiter(max_calls=max_calls, window_seconds=60.0)
    results = []
    lock = threading.Lock()

    def try_acquire():
        result = rl.acquire(block=False)
        with lock:
            results.append(result)

    threads = [threading.Thread(target=try_acquire) for _ in range(20)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert results.count(True) == max_calls
    assert results.count(False) == 10
