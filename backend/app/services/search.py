"""
Search / Filter builder for Events
==================================

Converts an `EventFilter` (Pydantic) + extra kwargs into a **SQLAlchemy
select()** statement which can be executed, paginated, or further joined
by calling code.

Why a separate builder?
-----------------------
* Keeps `crud.events.list_events()` readable
* Central spot to evolve search logic (full-text, popularity, etc.)
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import and_, desc, func, or_, select, text
from sqlmodel import Session

from app.models.booking import Booking
from app.models.event import Event
from app.models.slot import Slot
from app.schemas.event import EventFilter, SortOption


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def build_event_query(
    session: Session,
    filters: EventFilter,
) -> tuple:
    """
    Return **(select_stmt, count_stmt)** for events with given filters.

    The caller decides about pagination (`offset` / `limit`).
    """
    stmt = select(Event)

    # ————— TEXT SEARCH (title / desc / host) ——————————
    if filters.search:
        term = f"%{filters.search.lower()}%"
        if session.get_bind().dialect.name == "postgresql":
            # Use ILIKE for small data; full-text can replace later
            stmt = stmt.where(
                or_(
                    func.lower(Event.title).ilike(term),
                    func.lower(Event.description).ilike(term),
                    func.lower(Event.host_name).ilike(term),
                )
            )
        else:  # SQLite fallback
            stmt = stmt.where(
                or_(
                    func.lower(Event.title).like(term),
                    func.lower(Event.description).like(term),
                    func.lower(Event.host_name).like(term),
                )
            )

    # ————— CATEGORY ————————————————————————————————
    if filters.category:
        stmt = stmt.where(Event.category == filters.category)

    # ————— PRICE RANGE ——————————————————————————————
    if filters.price_min is not None:
        stmt = stmt.where(Event.price_minor >= filters.price_min)
    if filters.price_max is not None:
        stmt = stmt.where(Event.price_minor <= filters.price_max)

    # ————— SORTING ————————————————————————————————
    stmt = _apply_sort(stmt, filters.sort)

    # Build count() statement before pagination
    count_stmt = select(func.count()).select_from(stmt.subquery())

    return stmt, count_stmt


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _apply_sort(stmt, sort: SortOption | str):
    """
    Add ORDER BY clauses depending on the selected sort option.
    """
    option = sort if isinstance(sort, str) else sort.value

    if option == "price":
        return stmt.order_by(Event.price_minor.asc())
    if option == "rating":
        return stmt.order_by(
            Event.rating_avg.desc().nullslast(), Event.created_at.desc()
        )
    if option == "popularity":
        # Popularity = confirmed bookings in last 30 days
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        popularity_sub = (
            select(
                Slot.event_id.label("pop_event_id"),
                func.count(Booking.id).label("pop_count"),
            )
            .join(Booking, Booking.slot_id == Slot.id)
            .where(
                Booking.status == "CONFIRMED",
                Booking.booked_at >= thirty_days_ago,
            )
            .group_by(Slot.event_id)
            .subquery()
        )

        stmt = (
            stmt.join(
                popularity_sub,
                Event.id == popularity_sub.c.pop_event_id,
                isouter=True,
            )
            .order_by(popularity_sub.c.pop_count.desc().nullslast())
            .order_by(Event.created_at.desc())
        )
        return stmt

    # Default: recent
    return stmt.order_by(Event.created_at.desc())
