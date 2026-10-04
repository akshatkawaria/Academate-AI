"""
In-memory cache with TTL.
Lightweight — no Redis dependency needed.
"""
import time
from typing import Any, Optional

_store: dict[str, tuple[Any, float]] = {}

def get(key: str) -> Optional[Any]:
    if key in _store:
        value, expires_at = _store[key]
        if time.time() < expires_at:
            return value
        del _store[key]
    return None

def set(key: str, value: Any, ttl_seconds: int = 60):
    _store[key] = (value, time.time() + ttl_seconds)

def clear():
    _store.clear()
