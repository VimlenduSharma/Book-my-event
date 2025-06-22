"""
Thin Redis wrapper used by WebSocket broadcaster & services.
"""

import json
import logging
from typing import Any

import redis

from app.core.config import settings

log = logging.getLogger(__name__)

# Single global connection (thread-safe in redis-py ≥4)
redis_conn: redis.Redis = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)


def redis_publish(channel: str, message: str | dict[str, Any]) -> None:
    """
    Publish helper that accepts str **or** dict (auto-json encoded).
    """
    try:
        payload = message if isinstance(message, str) else json.dumps(message)
        redis_conn.publish(channel, payload)
    except Exception:  # pragma: no cover
        log.exception("Failed to publish Redis message")
