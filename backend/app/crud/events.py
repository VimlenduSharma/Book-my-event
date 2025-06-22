"""
Event CRUD helpers
==================

All DB-facing logic for the Event domain lives here so that
routers / services stay skinny and pure-business.

Functions
---------
create_event()          – POST /events
get_event()             – GET  /events/{id}
list_events()           – GET  /events   (with filters)
update_event()          – PATCH /events/{id}
delete_event()          – DELETE /events/{id}
recompute_event_rating()– called after each review
"""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional, Sequence, Tuple

from sqlalchemy import and_, desc, func, select, text
from sqlalchemy.orm import joinedload, selectinload
from sqlmodel import Session

from app.models.booking import Booking
from app.models.event import Event
from app.models.review import Review
from app.models.slot import Slot


# ────────────────────────────────────────────────────────────────
# Creation
# ────────────────────────────────────────────────────────────────


def create_event(
    session: Session,
    *,
    title: str,
    description: str,
    host_name: str,
    category: str,
    duration_min: int,
    price_minor: int,
    currency: str,
    timezone: str,
    image_url: Optional[str],
    slots: Sequence[dict],
) -> Event:
    """
    Inserts an Event **with** its Slot rows in one transaction.

    `slots` must be an iterable of  ❰{"start_utc": datetime, "max_bookings": int}❱
    objects (they’ve already been validated by the schema layer).
    """
    event = Event(
        title=title,
        description=description,
        host_name=host_name,
        category=category,
        duration_min=duration_min,
        price_minor=price_minor,
        currency=currency,
        timezone=timezone,
        image_url=image_url,
        created_at=datetime.utcnow(),
    )
    session.add(event)
    session.flush()  # assigns PK

    session.add_all(
        [
            Slot(
                event_id=event.id,
                start_utc=slot["start_utc"],
                max_bookings=slot.get("max_bookings", 1),
            )
            for slot in slots
        ]
    )
    session.commit()
    session.refresh(event)
    return event


# ────────────────────────────────────────────────────────────────
# Read helpers
# ────────────────────────────────────────────────────────────────


def get_event(session: Session, event_id: str) -> Optional[Event]:
    """
    Returns an Event with eagerly-loaded slots & reviews or None.
    """
    stmt = (
        select(Event)
        .options(
            selectinload(Event.slots),
            selectinload(Event.reviews),
        )
        .where(Event.id == event_id)
    )
    return session.exec(stmt).one_or_none()


# Pagination returns (objects, total_count)
def list_events(
    session: Session,
    *,
    page: int = 1,
    size: int = 20,
    search: Optional[str] = None,
    category: Optional[str] = None,
    price_min: Optional[int] = None,
    price_max: Optional[int] = None,
    sort: str = "recent",  # recent | price | rating | popularity
) -> Tuple[List[Event], int]:
    """
    Flexible listing with filters & sorting.

    * `search` does ILIKE on title / description / host
    * `price_min`/`price_max` filter by stored minor units
    """
    stmt = select(Event)

    # — Filters —
    from app.services.search import build_event_query 
    stmt, count_stmt = build_event_query(session, filters=EventFilter(page=page, size=size, search=search, 
                                                                      category=category, 
                                                                      price_min=price_min, price_max=price_max, sort=sort))

    # — Sorting —
    match sort:
        case "price":
            stmt = stmt.order_by(Event.price_minor.asc())
        case "rating":
            stmt = stmt.order_by(Event.rating_avg.desc().nullslast())
        case "popularity":
            # popularity = confirmed bookings in last 30 days
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            popularity_sub = (
                select(Booking.slot_id, func.count(Booking.id).label("pop"))
                .where(
                    Booking.booked_at >= thirty_days_ago,
                    Booking.status == "CONFIRMED",
                )
                .group_by(Booking.slot_id)
                .subquery()
            )
            stmt = (
                stmt.join(
                    popularity_sub,
                    popularity_sub.c.slot_id == Slot.id,
                    isouter=True,
                )
                .order_by(popularity_sub.c.pop.desc().nullslast())
                .order_by(Event.created_at.desc())
            )
        case _:
            stmt = stmt.order_by(Event.created_at.desc())

    # — Pagination —
    total = session.exec(select(func.count()).select_from(stmt.subquery())).scalar_one()
    stmt = (
        stmt.options(selectinload(Event.slots))
        .offset((page - 1) * size)
        .limit(size)
    )
    events = session.exec(stmt).all()
    return events, total


# ────────────────────────────────────────────────────────────────
# Update / delete
# ────────────────────────────────────────────────────────────────


def update_event(session: Session, event: Event, **data) -> Event:
    """
    Patch‐style update; only keys present in `data` are updated.
    """
    for key, value in data.items():
        if hasattr(event, key) and value is not None:
            setattr(event, key, value)
    session.add(event)
    session.commit()
    session.refresh(event)
    return event


def delete_event(session: Session, event: Event) -> None:
    session.delete(event)
    session.commit()


# ────────────────────────────────────────────────────────────────
# Ratings helper
# ────────────────────────────────────────────────────────────────


def recompute_event_rating(session: Session, event_id: str) -> None:
    """
    Re-aggregates average and count into the denormalised columns.
    Call after each review add/delete.
    """
    stats = (
        session.exec(
            select(
                func.avg(Review.rating).label("avg"),
                func.count(Review.id).label("cnt"),
            ).where(Review.event_id == event_id)
        )
        .first()
        or (None, 0)
    )
    avg, cnt = stats
    session.exec(
        (
            Event.__table__.update()
            .where(Event.id == event_id)
            .values(rating_avg=avg, rating_count=cnt)
        )
    )
    session.commit()
