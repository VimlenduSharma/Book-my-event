from __future__ import annotations

"""Celery tasks responsible for outbound e‑mails
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Current tasks
-------------
• **send_booking_email** – fire on new booking (or status change)
    – Generates body + subject
    – Adds Google Calendar quick‑add link and .ics download link
    – Uses services.email.send_email_plain

Extend this file with additional notification or digest tasks as needed.
"""

import logging
from textwrap import dedent
from typing import Optional

from sqlmodel import Session

from app.core.celery_app import celery_app
from app.core.database import get_session
from app.models.booking import Booking
from app.services.calendar import (
    google_calendar_link,
    upload_ics_and_return_url,
)
from app.services.email import send_email_plain

log = logging.getLogger(__name__)


# --------------------------------------------------------------------------------------------------
# Helper – fetch booking with eager‑loaded slot + event
# --------------------------------------------------------------------------------------------------

def _fetch_booking(session: Session, booking_id: str) -> Optional[Booking]:
    from sqlalchemy.orm import selectinload
    from sqlmodel import select

    stmt = (
        select(Booking)
        .where(Booking.id == booking_id)
        .options(
            selectinload(Booking.slot).selectinload("event")  # slot → event
        )
    )
    return session.exec(stmt).one_or_none()


# --------------------------------------------------------------------------------------------------
# Celery task
# --------------------------------------------------------------------------------------------------


@celery_app.task(name="email.send_booking_email", acks_late=True, max_retries=3)
def send_booking_email(booking_id: str) -> None:  # noqa: D401
    """Send confirmation e‑mail for a booking.

    *Retries* up to 3× on network errors.
    """

    with get_session() as session:
        booking = _fetch_booking(session, booking_id)
        if booking is None:
            log.error("send_booking_email: booking %s not found", booking_id)
            return

        slot = booking.slot
        event = slot.event

    # Calendar links / attachments
    gcal_link = google_calendar_link(booking)
    ics_url = upload_ics_and_return_url(booking)

    # Craft e‑mail
    subject = f"Confirmed: {event.title} on {slot.start_utc:%Y-%m-%d %H:%M UTC}"
    body = dedent(
        f"""
        Hi {booking.name},

        Your booking for **{event.title}** is confirmed!

        • 📆  Date & Time (UTC): {slot.start_utc:%A, %d %B %Y %H:%M}
        • ⏱   Duration         : {event.duration_min} min
        • 🧑‍💼  Host             : {event.host_name}

        ─────────────────────────────────────────────────
        Add to Google Calendar → {gcal_link}
        Download .ics           → {ics_url}
        ─────────────────────────────────────────────────

        Need to cancel? Just click the link in your dashboard.

        Cheers,
        Scheduler Bot
        """
    ).strip()

    try:
        send_email_plain(
            to=booking.email,
            subject=subject,
            body=body,
        )
        log.info("Booking confirmation sent to %s", booking.email)
    except Exception:  # pragma: no cover
        log.exception("Failed to send booking e‑mail to %s", booking.email)
        raise  # will trigger Celery retry
