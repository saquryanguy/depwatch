"""Simple file-based cache for changelog and metadata fetches."""

import hashlib
import json
import os
import time
from pathlib import Path
from typing import Any, Optional

DEFAULT_CACHE_DIR = Path(".depwatch_cache")
DEFAULT_TTL_SECONDS = 3600  # 1 hour


def _cache_key(namespace: str, identifier: str) -> str:
    """Generate a safe filename from namespace and identifier."""
    raw = f"{namespace}:{identifier}"
    digest = hashlib.sha256(raw.encode()).hexdigest()[:16]
    return f"{namespace}_{digest}.json"


def get_cached(namespace: str, identifier: str, ttl: int = DEFAULT_TTL_SECONDS,
               cache_dir: Path = DEFAULT_CACHE_DIR) -> Optional[Any]:
    """Return cached value if it exists and has not expired, else None."""
    cache_dir.mkdir(parents=True, exist_ok=True)
    path = cache_dir / _cache_key(namespace, identifier)
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if time.time() - data["timestamp"] > ttl:
            path.unlink(missing_ok=True)
            return None
        return data["value"]
    except (KeyError, json.JSONDecodeError, OSError):
        return None


def set_cached(namespace: str, identifier: str, value: Any,
               cache_dir: Path = DEFAULT_CACHE_DIR) -> None:
    """Persist a value to the cache."""
    cache_dir.mkdir(parents=True, exist_ok=True)
    path = cache_dir / _cache_key(namespace, identifier)
    payload = {"timestamp": time.time(), "value": value}
    path.write_text(json.dumps(payload), encoding="utf-8")


def clear_cache(cache_dir: Path = DEFAULT_CACHE_DIR) -> int:
    """Delete all cache entries. Returns number of files removed."""
    if not cache_dir.exists():
        return 0
    removed = 0
    for entry in cache_dir.glob("*.json"):
        try:
            entry.unlink()
            removed += 1
        except OSError:
            pass
    return removed


def cache_stats(cache_dir: Path = DEFAULT_CACHE_DIR) -> dict:
    """Return basic stats about the current cache directory."""
    if not cache_dir.exists():
        return {"entries": 0, "size_bytes": 0}
    entries = list(cache_dir.glob("*.json"))
    total_size = sum(e.stat().st_size for e in entries if e.exists())
    return {"entries": len(entries), "size_bytes": total_size}
