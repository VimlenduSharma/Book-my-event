"""
Review model
============

Stores a 1-to-5 star rating (and optional comment) that a user leaves
*after* attending an Event.  One review is linked to exactly one Booking,
and vice-versa.

Relationships
-------------
Event   1─∞  Review
Booking 1─1  Review   (Booking.review.uselist = False)
"""

from __future__ import annotations

from datetime import datetime
from uuid import uuid4
from typing import Optional

from sqlmodel import SQLModel, Field, Relationship


class Review(SQLModel, table=True):
    __tablename__ = "review"

    # ——— Columns ————————————————————————————————————————————
    id: str = Field(
        default_factory=lambda: str(uuid4()),
        primary_key=True,
        index=True,
    )

    event_id: str = Field(
        foreign_key="event.id",
        nullable=False,
        index=True,
        description="Parent event UUID",
    )
    booking_id: str = Field(
        foreign_key="booking.id",
        nullable=False,
        index=True,
        description="Booking this review refers to (1-to-1)",
    )

    rating: int = Field(
        ge=1,
        le=5,
        nullable=False,
        description="Integer star rating, 1–5",
    )
    comment: Optional[str] = Field(
        default=None,
        description="Optional free-text feedback",
    )

    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="UTC timestamp",
    )

    # ——— Relationships ————————————————————————————————
    event: "Event" = Relationship(back_populates="reviews")
    booking: "Booking" = Relationship(back_populates="review")


# Deferred imports to avoid circular dependencies
from app.models.event import Event    # noqa: E402
from app.models.booking import Booking  # noqa: E402
