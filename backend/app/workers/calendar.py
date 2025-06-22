from __future__ import annotations

"""Celery tasks for (mocked) calendar sync
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This file pretends to interact with an external calendar provider.
In REAL production you would authenticate via OAuth, store refresh tokens
per user, and call Google / Outlook APIs.  For this mini‑Calendly we:

1.  Generate the iCalendar (.ics) file once (already handled in email worker)
2.  Provide a *mock* sync that just logs the event – useful for demos
3.  Offer a `revoke_calendar_event` to show how cancellations could propagate

Feel free to swap the `log.debug` lines with real API calls later.
"""

import json
import logging
from enum import Enum

from sqlmodel import Session

from app.core.celery_app import celery_app
from app.core.database import get_session
from app.models.booking import Booking, BookingStatus
from app.services.calendar import generate_ics_bytes

log = logging.getLogger(__name__)


class CalendarAction(str, Enum):
    CREATE = "create"
    CANCEL = "cancel"


# --------------------------------------------------------------------------------------------------
# Helper – load booking + slot + event
# --------------------------------------------------------------------------------------------------

def _booking_with_event(booking_id: str) -> Booking | None:
    from sqlalchemy.orm import selectinload
    from sqlmodel import select

    with get_session() as session:
        stmt = (
            select(Booking)
            .where(Booking.id == booking_id)
            .options(selectinload(Booking.slot).selectinload("event"))
        )
        return session.exec(stmt).one_or_none()


# --------------------------------------------------------------------------------------------------
# Celery task: mock calendar sync
# --------------------------------------------------------------------------------------------------


@celery_app.task(name="calendar.sync_booking", acks_late=True, max_retries=2)
def sync_booking_with_calendar(booking_id: str, action: str = CalendarAction.CREATE) -> None:  # noqa: D401
    """Pretend to sync a booking with Google Calendar.

    The *front‑end* already has an *Add to Google Calendar* link.
    This task is just a stretch‑goal demo – called by the webhook or
    service layer if you want server‑side push.
    """

    booking = _booking_with_event(booking_id)
    if booking is None:
        log.error("calendar.sync_booking: booking %s not found", booking_id)
        return

    slot = booking.slot
    event = slot.event

    payload = {
        "summary": event.title,
        "description": event.description,
        "startUTC": slot.start_utc.isoformat(),
        "endUTC": (slot.start_utc + event.duration_min * 60).isoformat(),
        "attendee": booking.email,
        "action": action,
    }

    # In a real implementation you'd call requests/google‑client here
    log.debug("[MOCK] Pushing to calendar API: %s", json.dumps(payload))


# --------------------------------------------------------------------------------------------------
# Celery task: generate & cache .ics (optional)
# --------------------------------------------------------------------------------------------------


@celery_app.task(name="calendar.cache_ics", ignore_result=True)
def cache_ics_in_background(booking_id: str) -> None:  # noqa: D401
    """Generate .ics and keep in Redis or filesystem cache.

    This is optional; front‑end already can download via endpoint.
    """

    booking = _booking_with_event(booking_id)
    if booking is None or booking.status != BookingStatus.CONFIRMED:
        return

    try:
        ics_bytes = generate_ics_bytes(booking)
        path = f"/tmp/ics_cache/{booking.id}.ics"
        from pathlib import Path

        Path(path).parent.mkdir(parents=True, exist_ok=True)
        Path(path).write_bytes(ics_bytes)
        log.debug("Cached .ics at %s", path)
    except Exception:  # pragma: no cover
        log.exception("Failed to cache .ics for %s", booking.id)
