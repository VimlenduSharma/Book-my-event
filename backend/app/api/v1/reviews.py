from __future__ import annotations

"""api/v1/reviews.py – Router for Review endpoints"""

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlmodel import Session

from app.api.deps import db_session, pagination
from app.crud import get_booking as crud_get_booking
from app.crud import get_review as crud_get_review
from app.schemas import ReviewCreate, ReviewRead, ReviewUpdate
from app.services.review import (
    add_review,
    edit_review,
    event_reviews,
    remove_review,
)

router = APIRouter(prefix="", tags=["reviews"])

# ---------------------------------------------------------------------------
# CREATE  /events/{event_id}/reviews
# ---------------------------------------------------------------------------

@router.post(
    "/events/{event_id}/reviews",
    response_model=ReviewRead,
    status_code=status.HTTP_201_CREATED,
)
def create_review(
    event_id: str,
    payload: ReviewCreate,
    session: Session = Depends(db_session),
):
    # 1. ensure booking exists
    booking = crud_get_booking(session, payload.booking_id)
    if booking is None or booking.slot.event_id != event_id:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Invalid booking for event")

    review = add_review(
        session,
        booking=booking,
        rating=payload.rating,
        comment=payload.comment,
    )
    return ReviewRead.from_orm(review)


# ---------------------------------------------------------------------------
# LIST   /events/{event_id}/reviews
# ---------------------------------------------------------------------------

@router.get("/events/{event_id}/reviews", response_model=list[ReviewRead])
def list_event_reviews(
    event_id: str,
    page_info: tuple[int, int] = Depends(pagination),
    response: Response | None = None,  # type: ignore[valid-type]
    session: Session = Depends(db_session),
):
    page, size = page_info
    reviews, total = event_reviews(session, event_id=event_id, page=page, size=size)
    if response is not None:
        response.headers["X-Total"] = str(total)
    return [ReviewRead.from_orm(r) for r in reviews]


# ---------------------------------------------------------------------------
# UPDATE  /reviews/{id}
# ---------------------------------------------------------------------------

@router.patch("/reviews/{review_id}", response_model=ReviewRead)
def update_review(
    review_id: str,
    payload: ReviewUpdate,
    session: Session = Depends(db_session),
):
    review = crud_get_review(session, review_id)
    if review is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Review not found")

    updated = edit_review(
        session,
        review=review,
        rating=payload.rating,
        comment=payload.comment,
    )
    return ReviewRead.from_orm(updated)


# ---------------------------------------------------------------------------
# DELETE  /reviews/{id}
# ---------------------------------------------------------------------------

@router.delete("/reviews/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_review(review_id: str, session: Session = Depends(db_session)):
    review = crud_get_review(session, review_id)
    if review is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Review not found")

    remove_review(session, review=review)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
