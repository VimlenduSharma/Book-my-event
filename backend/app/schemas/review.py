"""
Pydantic / IO schemas for Review endpoints
=========================================

Used by:
* POST   /events/{id}/reviews        (create)
* GET    /events/{id}/reviews        (list)
* PATCH  /reviews/{id}               (optional update)

All date-times are ISO-8601 in **UTC**.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, conint


# ─────────────────────────────
# Create
# ─────────────────────────────


class ReviewCreate(BaseModel):
    """
    Payload for **POST /events/{event_id}/reviews**

    The `booking_id` is supplied because only attendees can review.
    """

    booking_id: str = Field(..., description="Booking UUID that grants review rights")
    rating: conint(ge=1, le=5) = Field(..., description="Stars 1–5")
    comment: Optional[str] = Field(None, max_length=2_000)


# ─────────────────────────────
# Update (PATCH)
# ─────────────────────────────


class ReviewUpdate(BaseModel):
    rating: Optional[conint(ge=1, le=5)] = None
    comment: Optional[str] = Field(None, max_length=2_000)


# ─────────────────────────────
# Read (outbound)
# ─────────────────────────────


class ReviewRead(BaseModel):
    id: str
    event_id: str
    booking_id: str
    rating: int
    comment: Optional[str]
    created_at: datetime

    class Config:
        orm_mode = True
