"""
Event model
===========

Represents a public event that visitors can book.

Key features
------------
* UUID primary key
* UTC `created_at`
* Denormalised `rating_avg` + `rating_count`
* `search_vector` column (PostgreSQL only) for full-text search
* Relationships:
    Event 1─∞ Slot
    Event 1─∞ Review
"""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional
from uuid import uuid4

from sqlalchemy import Column, String
from sqlmodel import Field, Relationship, SQLModel

# Conditional import → lets the model still be imported when
# you're running on SQLite (dialect has no TSVECTOR type).
try:
    from sqlalchemy.dialects.postgresql import TSVECTOR
except ImportError:  # pragma: no cover
    TSVECTOR = String  # type: ignore[assignment]


class Event(SQLModel, table=True):
    __tablename__ = "event"

    # ——— Basic columns ————————————————————————————
    id: str = Field(
        default_factory=lambda: str(uuid4()),
        primary_key=True,
        index=True,
        description="UUID primary key",
    )

    title: str = Field(nullable=False, sa_column=Column("title", String, index=True))
    description: str = Field(nullable=False, sa_column=Column(String))
    host_name: str = Field(nullable=False, sa_column=Column(String, index=True))
    category: str = Field(nullable=False, index=True)
    duration_min: int = Field(nullable=False, gt=0, description="Event length in minutes")

    # ——— Pricing ————————————————————————————————
    price_minor: int = Field(
        nullable=False,
        ge=0,
        description="Price in the smallest currency unit (cents/paisa)",
    )
    currency: str = Field(
        default="USD",
        min_length=3,
        max_length=3,
        description="ISO-4217 currency code",
    )

    # ——— Ratings (denormalised) ————————————————————
    rating_avg: Optional[float] = Field(
        default=None, description="Mean rating 1-5 (None until first review)"
    )
    rating_count: int = Field(default=0, ge=0)

    # ——— Other metadata ————————————————————————
    timezone: str = Field(nullable=False, description="IANA TZ (e.g. Europe/Paris)")
    image_url: Optional[str] = Field(
        default=None, description="Public URL of branding image"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        description="UTC creation timestamp",
    )

    # ——— Full-text search column (Postgres) —————————
    search_vector: Optional[str] = Field(
        sa_column=Column(
            "search_vector",
            TSVECTOR,          # TSVECTOR in PG, fallback to String on SQLite
            nullable=True,
        ),
        repr=False,
        index=True,
    )

    # ——— Relationships ————————————————————————
    slots: List["Slot"] = Relationship(back_populates="event")
    reviews: List["Review"] = Relationship(back_populates="event")


# Forward-declared imports (avoid circular refs at import time)
from app.models.slot import Slot  # noqa: E402  (placed after Event class)
from app.models.review import Review  # noqa: E402
from app.models.category_enum import CategoryEnum
