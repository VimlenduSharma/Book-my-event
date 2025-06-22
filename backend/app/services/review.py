from app.crud import recompute_event_rating
recompute_event_rating(session, event_id=review.event_id)
from __future__ import annotations

"""Domain logic for Reviews
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Enforces business rules before delegating to CRUD helpers:
* Only one review per Booking.
* Booking must belong to the same event and be CONFIRMED.
* (Optional) Users can edit/delete only their own review – left to router.
"""

from datetime import datetime
from typing import Tuple, List, Optional

from fastapi import HTTPException, status
from sqlmodel import Session

from app.crud import (
    review_exists,
    create_review as crud_create_review,
    list_reviews as crud_list_reviews,
    delete_review as crud_delete_review,
    update_review as crud_update_review,
)
from app.models.booking import Booking, BookingStatus
from app.models.review import Review


# ---------------------------------------------------------------------------
# Creation
# ---------------------------------------------------------------------------

def add_review(
    session: Session,
    *,
    booking: Booking,
    rating: int,
    comment: Optional[str] = None,
) -> Review:
    """Add a review for a booking after validating rules."""

    if booking.status != BookingStatus.CONFIRMED:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail="Cannot review an unconfirmed booking.",
        )

    if review_exists(session, booking_id=booking.id):
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            detail="This booking already has a review.",
        )

    now = datetime.utcnow()
    # Optional: prevent reviewing future events – uncomment if desired
    # if booking.slot.start_utc > now:
    #     raise HTTPException(400, "You can only review after the event has occurred.")

    return crud_create_review(
        session,
        event_id=booking.slot.event_id,
        booking_id=booking.id,
        rating=rating,
        comment=comment,
    )


# ---------------------------------------------------------------------------
# Listing (with pagination)
# ---------------------------------------------------------------------------

def event_reviews(
    session: Session,
    *,
    event_id: str,
    page: int = 1,
    size: int = 20,
) -> Tuple[List[Review], int]:
    return crud_list_reviews(session, event_id=event_id, page=page, size=size)


# ---------------------------------------------------------------------------
# Update
# ---------------------------------------------------------------------------

def edit_review(
    session: Session,
    *,
    review: Review,
    rating: Optional[int] = None,
    comment: Optional[str] = None,
) -> Review:
    if rating is None and comment is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="No changes supplied.")

    return crud_update_review(session, review, rating=rating, comment=comment)


# ---------------------------------------------------------------------------
# Delete
# ---------------------------------------------------------------------------

def remove_review(session: Session, *, review: Review) -> None:
    crud_delete_review(session, review)
