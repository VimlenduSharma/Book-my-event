from __future__ import annotations

"""CRUD helpers for Review domain
----------------------------------
Routers & services should use ONLY these helpers when touching the
`review` table so that rating roll‑ups stay consistent.
"""

from datetime import datetime
from typing import List, Optional, Tuple

from sqlalchemy import func, select
from sqlalchemy.orm import selectinload
from sqlmodel import Session

from app.crud.events import recompute_event_rating
from app.models.review import Review

# ---------------------------------------------------------------------------
# Helpers / constraints
# ---------------------------------------------------------------------------

def review_exists(session: Session, *, booking_id: str) -> bool:
    """Return **True** if a review already exists for this booking."""
    stmt = select(func.count()).select_from(Review).where(Review.booking_id == booking_id)
    return session.exec(stmt).scalar_one() > 0


# ---------------------------------------------------------------------------
# CRUD operations
# ---------------------------------------------------------------------------

def create_review(
    session: Session,
    *,
    event_id: str,
    booking_id: str,
    rating: int,
    comment: Optional[str] = None,
) -> Review:
    if review_exists(session, booking_id=booking_id):
        raise ValueError("This booking already has a review.")

    review = Review(
        event_id=event_id,
        booking_id=booking_id,
        rating=rating,
        comment=comment,
        created_at=datetime.utcnow(),
    )
    session.add(review)
    session.commit()
    session.refresh(review)

    recompute_event_rating(session, event_id)
    return review


def get_review(session: Session, review_id: str) -> Optional[Review]:
    stmt = select(Review).where(Review.id == review_id)
    return session.exec(stmt).one_or_none()


def list_reviews(
    session: Session,
    *,
    event_id: str,
    page: int = 1,
    size: int = 20,
) -> Tuple[List[Review], int]:
    stmt = (
        select(Review)
        .where(Review.event_id == event_id)
        .order_by(Review.created_at.desc())
        .options(selectinload(Review.booking))
    )

    total = session.exec(select(func.count()).select_from(stmt.subquery())).scalar_one()
    reviews = session.exec(stmt.offset((page - 1) * size).limit(size)).all()
    return reviews, total


def update_review(session: Session, review: Review, **data) -> Review:
    for key, value in data.items():
        if value is not None and hasattr(review, key):
            setattr(review, key, value)
    session.add(review)
    session.commit()
    session.refresh(review)

    recompute_event_rating(session, review.event_id)
    return review


def delete_review(session: Session, review: Review) -> None:
    event_id = review.event_id
    session.delete(review)
    session.commit()
    recompute_event_rating(session, event_id)
