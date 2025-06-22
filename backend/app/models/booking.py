"""
Booking model
=============

Captures a visitor’s reservation for a specific Slot.

Rules enforced
--------------
* One-per-user-per-slot → UNIQUE (slot_id, email)
* Status enum  :  CONFIRMED | CANCELLED
* UTC timestamp for created row
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import uuid4

from sqlalchemy import Column, DateTime, String, UniqueConstraint
from sqlmodel import Field, Relationship, SQLModel


class BookingStatus(str, Enum):
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"


class Booking(SQLModel, table=True):
    __tablename__ = "booking"
    __table_args__ = (
        UniqueConstraint(
            "slot_id",
            "email",
            name="uix_slot_email",
        ),
    )

    # ——— Core columns ————————————————————————————
    id: str = Field(
        default_factory=lambda: str(uuid4()),
        primary_key=True,
        index=True,
    )

    slot_id: str = Field(
        foreign_key="slot.id",
        nullable=False,
        index=True,
        description="FK to Slot",
    )

    name: str = Field(nullable=False, sa_column=Column(String))
    email: str = Field(nullable=False, sa_column=Column(String, index=True))

    status: BookingStatus = Field(
        default=BookingStatus.CONFIRMED,
        sa_column=Column(String),
        description="CONFIRMED | CANCELLED",
    )

    booked_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )

    # ——— Relationships ——————————————————————————
    slot: "Slot" = Relationship(back_populates="bookings")
    review: Optional["Review"] = Relationship(
        back_populates="booking",
        sa_relationship_kwargs={"uselist": False},
    )

    # ——— Convenience props ——————————————————————
    @property
    def is_active(self) -> bool:
        """Returns True if the booking hasn't been cancelled."""
        return self.status == BookingStatus.CONFIRMED
        

# ——— Deferred imports to avoid circular refs —————————
from app.models.slot import Slot      # noqa: E402
from app.models.review import Review  # noqa: E402
