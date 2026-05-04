import hashlib
import json
import logging
from typing import Any

from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger("trips.maps")


def build_cache_key(namespace: str, payload: Any) -> str:
    payload_json = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    payload_digest = hashlib.sha256(payload_json.encode("utf-8")).hexdigest()
    return f"trips:{namespace}:{payload_digest}"


def get_cached_value(namespace: str, payload: Any) -> Any:
    cache_key = build_cache_key(namespace, payload)
    try:
        return cache.get(cache_key)
    except Exception as error:
        logger.warning(
            "maps_cache_read_failed namespace=%s key=%s error=%s",
            namespace,
            cache_key,
            error,
        )
        return None


def set_cached_value(namespace: str, payload: Any, value: Any) -> Any:
    cache_key = build_cache_key(namespace, payload)
    try:
        cache.set(cache_key, value, timeout=settings.MAPS_CACHE_TTL_SECONDS)
    except Exception as error:
        logger.warning(
            "maps_cache_write_failed namespace=%s key=%s error=%s",
            namespace,
            cache_key,
            error,
        )
    return value
