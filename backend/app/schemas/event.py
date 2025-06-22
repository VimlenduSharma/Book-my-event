"""
Pydantic / IO schemas for Event endpoints
========================================

These *never* get persisted directly—SQLModel tables live in `app.models.*`.
They are only used for request validation and OpenAPI generation.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, conint, constr, validator


# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────


class Currency(str, Enum):
    """Subset of ISO-4217 used in the UI currency switcher."""
    USD = "USD"
    EUR = "EUR"
    INR = "INR"
    GBP = "GBP"


# ──────────────────────────────────────────────────────────────────────────────
# Slot sub-schemas  (nested inside EventCreate / EventDetail)
# ──────────────────────────────────────────────────────────────────────────────


class SlotInput(BaseModel):
    """
    Incoming slot from the *Create Event* wizard.
    Front-end converts local time → UTC before POST.
    """

    start_utc: datetime = Field(
        ...,
        description="Slot start in UTC (ISO-8601)",
        example="2025-06-20T10:00:00Z",
    )
    max_bookings: conint(gt=0) = Field(
        1,
        description="Capacity for this slot",
        example=5,
    )


class SlotRead(BaseModel):
    """
    Returned inside EventDetail so the calendar can be rendered.
    """

    id: str
    start_utc: datetime
    remaining: int
    is_full: bool

    class Config:
        orm_mode = True


# ──────────────────────────────────────────────────────────────────────────────
# Core Event schemas
# ──────────────────────────────────────────────────────────────────────────────


class _EventBase(BaseModel):
    title: str = Field(..., max_length=140)
    description: str
    host_name: str
    category: str = Field(..., example="Design")
    duration_min: conint(gt=0) = Field(..., example=90)
    price_minor: conint(ge=0) = Field(..., description="Smallest unit e.g. cents")
    currency: Currency = Field(Currency.USD)
    timezone: str = Field(..., example="America/New_York")
    image_url: Optional[str] = Field(
        None,
        description="S3 public URL (filled by backend after presign upload)",
    )


# ———  create  ————————————————————————————————————————————


class EventCreate(_EventBase):
    """
    Payload for **POST /events**.
    """

    slots: List[SlotInput] = Field(
        ...,
        min_items=1,
        description="List of time slots in UTC",
    )


# ———  update / patch  —————————————————————————————————————————


class EventUpdate(BaseModel):
    """
    Partial update; every field is optional.
    """

    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    duration_min: Optional[conint(gt=0)] = None
    price_minor: Optional[conint(ge=0)] = None
    currency: Optional[Currency] = None
    timezone: Optional[str] = None
    image_url: Optional[str] = None


# ———  outbound / list view  ————————————————————————————


class EventCard(_EventBase):
    """
    Compact card for the home grid.
    """

    id: str
    remaining_slots: int
    rating_avg: Optional[float] = None
    rating_count: int

    class Config:
        orm_mode = True


# ———  outbound / detail view  ———————————————————————————


class EventDetail(EventCard):
    """
    Full detail page (slots included).
    """

    created_at: datetime
    slots: List[SlotRead]

    class Config:
        orm_mode = True


# ──────────────────────────────────────────────────────────────────────────────
# Query-param helper  (for GET /events? …)
# ──────────────────────────────────────────────────────────────────────────────


class SortOption(str, Enum):
    recent = "recent"
    price = "price"
    rating = "rating"
    popularity = "popularity"


class EventFilter(BaseModel):
    """
    FastAPI will turn this into query parameters automatically.
    """

    page: int = Field(1, ge=1)
    size: int = Field(20, le=100)
    search: Optional[str] = None
    category: Optional[str] = None
    price_min: Optional[int] = Field(None, ge=0)
    price_max: Optional[int] = Field(None, ge=0)
    sort: SortOption = SortOption.recent

    @validator("price_max")
    def price_range_valid(cls, v, values):
        if v is not None and values.get("price_min") is not None:
            if v < values["price_min"]:
                raise ValueError("price_max must be ≥ price_min")
        return v
