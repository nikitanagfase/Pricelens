"""
services/cache_service.py
─────────────────────────────────────────────
Wraps Redis so the rest of the app never has to
think about it. If Redis isn't installed/running
(very common in a student dev setup), this silently
falls back to a process-memory dict — same interface,
zero crashes, just no persistence across restarts.

Purpose: cache Ignav search results so we don't
burn the free monthly API quota on repeated identical
searches (same route+date within the TTL window).
"""
import json
import time
from typing import Optional, Any

from app.core.config import settings

_memory_store: dict[str, tuple[float, str]] = {}   # key -> (expires_at, json_value)

_redis_client = None
_redis_available = False

try:
    import redis as redis_lib
    _redis_client = redis_lib.from_url(settings.REDIS_URL, socket_connect_timeout=1)
    _redis_client.ping()
    _redis_available = True
except Exception:
    _redis_available = False


def cache_get(key: str) -> Optional[Any]:
    if _redis_available:
        try:
            val = _redis_client.get(key)
            return json.loads(val) if val else None
        except Exception:
            return None
    # in-memory fallback
    entry = _memory_store.get(key)
    if not entry:
        return None
    expires_at, value = entry
    if time.time() > expires_at:
        _memory_store.pop(key, None)
        return None
    return json.loads(value)


def cache_set(key: str, value: Any, ttl_seconds: int = 600):
    payload = json.dumps(value)
    if _redis_available:
        try:
            _redis_client.set(key, payload, ex=ttl_seconds)
            return
        except Exception:
            pass
    _memory_store[key] = (time.time() + ttl_seconds, payload)


def cache_status() -> str:
    return "redis" if _redis_available else "in-memory-fallback"
