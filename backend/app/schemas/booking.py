"""
Pydantic / IO schemas for Booking endpoints
==========================================

These are *transport-layer* only; persistence lives
in `app.models.booking.Booking`.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, constr


# ─────────────────────────────────────────────────────────────────────
# Shared Enums
# ─────────────────────────────────────────────────────────────────────

class BookingStatus(str, Enum):
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"


# ─────────────────────────────────────────────────────────────────────
# Base / mixin
# ─────────────────────────────────────────────────────────────────────

class _BookingBase(BaseModel):
    name: constr(min_length=1, max_length=80)
    email: EmailStr


# ─────────────────────────────────────────────────────────────────────
# Create  (client → server)
# ─────────────────────────────────────────────────────────────────────

class BookingCreate(_BookingBase):
    """
    Payload for **POST /events/{event_id}/bookings**.

    The parent event ID is supplied in the path; client sends
    the chosen slot UUID.
    """

    slot_id: str = Field(..., description="UUID of the selected slot")


# ─────────────────────────────────────────────────────────────────────
# Update  (PATCH / cancel)
# ─────────────────────────────────────────────────────────────────────

class BookingUpdate(BaseModel):
    status: BookingStatus = Field(
        ...,
        description="Only allowed transition: CONFIRMED ➜ CANCELLED",
    )


# ─────────────────────────────────────────────────────────────────────
# Read / outbound
# ─────────────────────────────────────────────────────────────────────

class BookingRead(_BookingBase):
    """
    Returned by list & detail endpoints.
    """

    id: str
    event_id: str
    slot_id: str
    event_title: str
    start_utc: datetime
    status: BookingStatus
    booked_at: datetime
    currency: str
    price_minor: int
    image_url: Optional[str] = None

    class Config:
        orm_mode = True
