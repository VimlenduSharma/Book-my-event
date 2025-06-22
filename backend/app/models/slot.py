"""
Slot model
==========

Represents a single bookable time-block linked to an Event.

Highlights
----------
* UUID primary key
* One-to-many   Event → Slot
* One-to-many   Slot  → Booking
* Unique (event_id, start_utc) constraint so the same
  date-time can’t be inserted twice for one event.
"""

from __future__ import annotations

from datetime import datetime
from typing import List
from uuid import uuid4

from sqlalchemy import Column, DateTime, UniqueConstraint
from sqlmodel import Field, Relationship, SQLModel


class Slot(SQLModel, table=True):
    __tablename__ = "slot"
    __table_args__ = (
        UniqueConstraint(
            "event_id",
            "start_utc",
            name="uix_event_start",
        ),
    )

    # ——— Core columns ————————————————————————————
    id: str = Field(
        default_factory=lambda: str(uuid4()),
        primary_key=True,
        index=True,
    )

    # FK → app.models.event.Event
    event_id: str = Field(
        foreign_key="event.id",
        nullable=False,
        index=True,
        description="Parent event UUID",
    )

    # Stored in UTC; indexed for fast range queries
    start_utc: datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=False, index=True),
        description="Slot start timestamp (UTC)",
    )

    max_bookings: int = Field(
        default=1,
        ge=1,
        description="Capacity for this slot",
    )

    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="UTC row creation time",
    )

    # ——— Relationships ——————————————————————————
    event: "Event" = Relationship(back_populates="slots")
    bookings: List["Booking"] = Relationship(back_populates="slot")

    # ——— Convenience props ——————————————————————
    @property
    def is_full(self) -> bool:
        """Returns True if the slot has reached max capacity."""
        return len(self.bookings) >= self.max_bookings

    @property
    def remaining(self) -> int:
        """Number of seats still open (never negative)."""
        return max(self.max_bookings - len(self.bookings), 0)


# ——— Deferred imports to avoid circular refs —————————
from app.models.event import Event  # noqa: E402  (after class definition)
from app.models.booking import Booking  # noqa: E402
