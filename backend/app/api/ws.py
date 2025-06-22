from __future__ import annotations

"""api/ws.py – WebSocket endpoint for realtime slot updates
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* 1️⃣  Client connects to `/ws/events/{event_id}` (or whatever path you mount)
* 2️⃣  Server subscribes to Redis channel `event:{event_id}`
* 3️⃣  Whenever `services.bookings._broadcast_slot_update()` publishes JSON,
       the server forwards it to all connected browsers.

Protocol (client ↔ server)
--------------------------
• **Send**: nothing (one‑way push)
• **Receive**: JSON objects, e.g.  `{ "slot_id": "…", "remaining": 4, "is_full": false }`

The client can keep the socket open and update its React state whenever a
message arrives.
"""

import asyncio
import json
import logging
from typing import Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.core.config import settings

# redis.asyncio is available in redis-py >=4.2
try:
    from redis.asyncio import Redis  # type: ignore
except ImportError as exc:  # pragma: no cover
    raise RuntimeError(
        "redis-py >=4.2 required for async WebSocket support – install `redis` package"
    ) from exc

log = logging.getLogger(__name__)

router = APIRouter()


# ----------------------------------------------------------------------------
# Helper: get (cached) Redis connection
# ----------------------------------------------------------------------------


_redis: Redis | None = None


def _get_redis() -> Redis:
    global _redis
    if _redis is None:
        _redis = Redis.from_url(settings.REDIS_URL, decode_responses=True)
    return _redis


# ----------------------------------------------------------------------------
# WebSocket endpoint
# ----------------------------------------------------------------------------


@router.websocket("/events/{event_id}/updates")
async def event_updates_ws(ws: WebSocket, event_id: str):
    """Push channel for live slot updates."""

    await ws.accept()
    redis = _get_redis()
    channel = f"event:{event_id}"

    try:
        pubsub = redis.pubsub()
        await pubsub.subscribe(channel)
        log.debug("WebSocket subscribed to %s", channel)

        # Simple ping loop (optional but keeps Heroku / nginx happy)
        async def _ping():
            while True:
                await asyncio.sleep(25)
                try:
                    await ws.send_text("\uD83D\uDC4B")  # 👋 heartbeat
                except WebSocketDisconnect:
                    break

        ping_task = asyncio.create_task(_ping())

        async for message in pubsub.listen():  # type: ignore[attr-defined]
            if message is None:
                continue
            if message["type"] != "message":
                continue
            payload = message["data"]
            # Ensure JSON string – redis-py may already give str
            if not isinstance(payload, str):
                payload = json.dumps(payload)
            try:
                await ws.send_text(payload)
            except WebSocketDisconnect:
                break
    finally:
        await ws.close()
        try:
            await pubsub.unsubscribe(channel)
            await pubsub.close()
        except Exception:  # pragma: no cover
            pass
        if not ws.client_state.name == "DISCONNECTED":
            log.debug("WebSocket for event %s disconnected", event_id)

        if ping_task and not ping_task.done():
            ping_task.cancel()
