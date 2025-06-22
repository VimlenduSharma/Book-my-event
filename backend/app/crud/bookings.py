"""
Booking CRUD helpers
====================

Routers and service-layers should call ONLY functions defined here when they
need to touch Booking rows.  That guarantees all business rules (no double
booking, capacity check, etc.) are enforced in *one* place.

Functions
---------
create_booking()          – create & return a new row
get_booking()             – fetch single row by UUID
booking_exists()          – bool helper (slot + email)
booking_count()           – #confirmed bookings for a slot
cancel_booking()          – set status → CANCELLED
list_user_bookings()      – paginated list for “My Bookings” page
"""

from __future__ import annotations

from datetime import datetime
from typing import List, Tuple

from sqlalchemy import func, select
from sqlalchemy.orm import selectinload
from sqlmodel import Session

from app.models.booking import Booking, BookingStatus
from app.models.event import Event
from app.models.slot import Slot

# ────────────────────────────────────────────────────────────────
# Create
# ────────────────────────────────────────────────────────────────


def create_booking(
    session: Session,
    *,
    slot_id: str,
    name: str,
    email: str,
) -> Booking:
    """
    Inserts a new CONFIRMED booking and returns it.

    Caller MUST have already validated:
    * capacity (booking_count < max_bookings)
    * uniqueness (booking_exists is False)
    """
    booking = Booking(
        slot_id=slot_id,
        name=name,
        email=email,
        status=BookingStatus.CONFIRMED,
        booked_at=datetime.utcnow(),
    )
    session.add(booking)
    session.commit()
    session.refresh(booking)
    return booking


# ────────────────────────────────────────────────────────────────
# Read helpers
# ────────────────────────────────────────────────────────────────


def get_booking(session: Session, booking_id: str) -> Booking | None:
    """
    Eager-loads slot + event so the response layer has everything.
    """
    stmt = (
        select(Booking)
        .where(Booking.id == booking_id)
        .options(
            selectinload(Booking.slot)
            .selectinload(Slot.event)  # chain: booking → slot → event
        )
    )
    return session.exec(stmt).one_or_none()


def booking_exists(session: Session, slot_id: str, email: str) -> bool:
    """
    Returns True if a CONFIRMED booking with this slot & e-mail already exists.
    """
    stmt = (
        select(func.count())
        .select_from(Booking)
        .where(
            Booking.slot_id == slot_id,
            Booking.email == email,
            Booking.status == BookingStatus.CONFIRMED,
        )
    )
    return session.exec(stmt).scalar_one() > 0


def booking_count(session: Session, slot_id: str) -> int:
    """
    CONFIRMED bookings only – used to check capacity.
    """
    stmt = (
        select(func.count())
        .select_from(Booking)
        .where(
            Booking.slot_id == slot_id,
            Booking.status == BookingStatus.CONFIRMED,
        )
    )
    return session.exec(stmt).scalar_one()


# ────────────────────────────────────────────────────────────────
# Update / cancel
# ────────────────────────────────────────────────────────────────


def cancel_booking(session: Session, booking: Booking) -> Booking:
    """
    Marks the row as CANCELLED (idempotent).
    """
    if booking.status == BookingStatus.CANCELLED:
        return booking
    booking.status = BookingStatus.CANCELLED
    session.add(booking)
    session.commit()
    session.refresh(booking)
    return booking


# ────────────────────────────────────────────────────────────────
# Listing helpers
# ────────────────────────────────────────────────────────────────


def list_user_bookings(
    session: Session,
    *,
    email: str,
    page: int = 1,
    size: int = 50,
) -> Tuple[List[Booking], int]:
    """
    Returns paginated bookings for “My bookings” (sorted newest first).
    """
    stmt = (
        select(Booking)
        .where(Booking.email == email)
        .options(
            selectinload(Booking.slot)
            .selectinload(Slot.event)
        )
        .order_by(Booking.booked_at.desc())
    )

    total = session.exec(
        select(func.count()).select_from(stmt.subquery())
    ).scalar_one()
    bookings = (
        session.exec(stmt.offset((page - 1) * size).limit(size))
        .all()
    )
    return bookings, total
