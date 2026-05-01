import hashlib
import json
from typing import Any

from django.conf import settings
from django.core.cache import cache


def build_cache_key(namespace: str, payload: Any) -> str:
    payload_json = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    payload_digest = hashlib.sha256(payload_json.encode("utf-8")).hexdigest()
    return f"trips:{namespace}:{payload_digest}"


def get_cached_value(namespace: str, payload: Any) -> Any:
    return cache.get(build_cache_key(namespace, payload))


def set_cached_value(namespace: str, payload: Any, value: Any) -> Any:
    cache_key = build_cache_key(namespace, payload)
    cache.set(cache_key, value, timeout=settings.MAPS_CACHE_TTL_SECONDS)
    return value
