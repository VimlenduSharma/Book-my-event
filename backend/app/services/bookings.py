"""
Business logic for bookings
===========================

Routers call these *only* — never touch CRUD or models directly.
That way every invariant (capacity, uniqueness, side-effects) is
enforced in a single spot.
"""

from __future__ import annotations

import json
from typing import Tuple

from fastapi import HTTPException, status
from sqlmodel import Session

from app.core.redis import redis_publish
from app.crud import (
    booking_count,
    booking_exists,
    cancel_booking as crud_cancel_booking,
    create_booking as crud_create_booking,
    get_booking,
)
from app.models.booking import Booking, BookingStatus
from app.models.slot import Slot
from app.workers.email import send_booking_email


# ────────────────────────────────────────────────────────────────
# Public API
# ────────────────────────────────────────────────────────────────


def make_booking(
    session: Session,
    *,
    slot: Slot,
    name: str,
    email: str,
) -> Booking:
    """
    Main entry used by POST /events/{id}/bookings
    """
    # —— business rules —————————————————————
    if booking_exists(session, slot.id, email):
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            detail="You have already booked this slot.",
        )

    if booking_count(session, slot.id) >= slot.max_bookings:
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            detail="Slot is already full.",
        )

    # —— persist ——————————————————————————————
    booking = crud_create_booking(
        session,
        slot_id=slot.id,
        name=name,
        email=email,
    )

    # —— side-effects (fire-and-forget) ——————————
    send_booking_email.delay(booking.id)
    _broadcast_slot_update(slot)

    return booking


def cancel_booking(
    session: Session,
    *,
    booking: Booking,
) -> Booking:
    """
    PATCH /bookings/{id} (caller has verified ownership / auth).
    """
    if booking.status == BookingStatus.CANCELLED:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail="Booking already cancelled.",
        )

    booking = crud_cancel_booking(session, booking)

    # rebroadcast remaining seats
    _broadcast_slot_update(booking.slot)
    return booking


def user_bookings(
    session: Session,
    *,
    email: str,
    page: int = 1,
    size: int = 50,
) -> Tuple[list[Booking], int]:
    """
    Thin wrapper around crud.list_user_bookings so future
    transforms (e.g. masking e-mail) go here once.
    """
    from app.crud import list_user_bookings  # local import avoids cycles

    return list_user_bookings(session, email=email, page=page, size=size)


# ────────────────────────────────────────────────────────────────
# Internal helpers
# ────────────────────────────────────────────────────────────────


def _broadcast_slot_update(slot: Slot) -> None:
    """
    Publishes `{slot_id, remaining}` to Redis channel
    `event:{event_id}` so WebSocket clients refresh UI.
    """
    payload = {
        "slot_id": slot.id,
        "remaining": slot.remaining,
        "is_full": slot.is_full,
    }
    channel = f"event:{slot.event_id}"
    redis_publish(channel, json.dumps(payload))
