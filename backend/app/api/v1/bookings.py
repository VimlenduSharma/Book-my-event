from __future__ import annotations

"""api/v1/bookings.py – FastAPI router for Booking endpoints
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Routes
------
POST   /events/{event_id}/bookings   – create a booking
GET    /users/{email}/bookings       – list bookings by e‑mail (My Bookings)
GET    /bookings/{id}                – get single booking detail
PATCH  /bookings/{id}                – cancel booking
GET    /bookings/{id}/ics            – download iCalendar file
"""

from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.responses import StreamingResponse
from sqlmodel import Session

from app.api.deps import db_session, required_email, pagination
from app.crud import get_booking as crud_get_booking
from app.models.slot import Slot
from app.schemas import (
    BookingCreate,
    BookingRead,
    BookingUpdate,
)
from app.services.bookings import (
    make_booking,
    user_bookings as svc_user_bookings,
    cancel_booking as svc_cancel_booking,
)
from app.services.calendar import generate_ics_bytes

router = APIRouter(prefix="", tags=["bookings"])

# ----------------------------------------------------------------------------
# CREATE under /events/{event_id}/bookings
# ----------------------------------------------------------------------------


@router.post(
    "/events/{event_id}/bookings",
    response_model=BookingRead,
    status_code=status.HTTP_201_CREATED,
)
def create_booking(
    event_id: str,
    payload: BookingCreate,
    session: Session = Depends(db_session),
):
    # Validate slot belongs to event
    slot: Slot | None = session.get(Slot, payload.slot_id)
    if slot is None or slot.event_id != event_id:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Invalid slot for event")

    booking = make_booking(
        session,
        slot=slot,
        name=payload.name,
        email=payload.email,
    )
    return BookingRead.from_orm(booking)


# ----------------------------------------------------------------------------
# LIST user bookings  /users/{email}/bookings
# ----------------------------------------------------------------------------


@router.get("/users/{email}/bookings", response_model=list[BookingRead])
def my_bookings(
    email: str,
    page_info: tuple[int, int] = Depends(pagination),
    session: Session = Depends(db_session),
):
    page, size = page_info
    bookings, total = svc_user_bookings(session, email=email, page=page, size=size)
    response = Response()
    response.headers["X-Total"] = str(total)
    return [BookingRead.from_orm(b) for b in bookings]


# ----------------------------------------------------------------------------
# DETAIL
# ----------------------------------------------------------------------------


@router.get("/bookings/{booking_id}", response_model=BookingRead)
def get_booking(booking_id: str, session: Session = Depends(db_session)):
    booking = crud_get_booking(session, booking_id)
    if not booking:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Booking not found")
    return BookingRead.from_orm(booking)


# ----------------------------------------------------------------------------
# CANCEL (PATCH)
# ----------------------------------------------------------------------------


@router.patch("/bookings/{booking_id}", response_model=BookingRead)
def cancel_booking_endpoint(
    booking_id: str,
    payload: BookingUpdate,
    session: Session = Depends(db_session),
):
    if payload.status != "CANCELLED":
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Only cancellation supported")

    booking = crud_get_booking(session, booking_id)
    if not booking:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Booking not found")

    updated = svc_cancel_booking(session, booking=booking)
    return BookingRead.from_orm(updated)


# ----------------------------------------------------------------------------
# ICS download
# ----------------------------------------------------------------------------


@router.get("/bookings/{booking_id}/ics")
def download_ics(booking_id: str, session: Session = Depends(db_session)):
    booking = crud_get_booking(session, booking_id)
    if not booking:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Booking not found")

    ics_bytes = generate_ics_bytes(booking)
    filename = f"{booking_id}.ics"
    return StreamingResponse(
        ics_bytes,
        media_type="text/calendar",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
