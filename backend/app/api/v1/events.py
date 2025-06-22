from __future__ import annotations

"""api/v1/events.py – FastAPI router for Event endpoints
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Routes
------
POST   /events                 – create a new event (with slots)
GET    /events                 – list events with filters & pagination
GET    /events/{id}            – retrieve a single event (detail)
PATCH  /events/{id}            – partial update (creator only)
DELETE /events/{id}            – delete event (optional, here for completeness)
POST   /events/{id}/image-url  – presign S3 upload URL for branding image
"""

from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, Header, HTTPException, Response, status
from sqlmodel import Session

from app.api.deps import db_session, pagination
from app.crud import (
    create_event as crud_create_event,
    delete_event as crud_delete_event,
    get_event as crud_get_event,
    list_events as crud_list_events,
    update_event as crud_update_event,
)
from app.schemas import (
    EventCard,
    EventCreate,
    EventDetail,
    EventFilter,
    EventUpdate,
)

# Optional: presign helper (S3 or MinIO)
try:
    from app.storage.presign import generate_event_image_urls  # type: ignore
except ImportError:  # pragma: no cover – storage layer may come later
    generate_event_image_urls = None  # type: ignore


router = APIRouter(prefix="/events", tags=["events"])


# ----------------------------------------------------------------------------
# LIST
# ----------------------------------------------------------------------------


@router.get("/", response_model=List[EventCard])
def list_events(
    filters: EventFilter = Depends(),
    response: Response = None,  # type: ignore
    session: Session = Depends(db_session),
):
    """Public listing with search, category & price filters."""

    events, total = crud_list_events(
        session,
        page=filters.page,
        size=filters.size,
        search=filters.search,
        category=filters.category,
        price_min=filters.price_min,
        price_max=filters.price_max,
        sort=filters.sort.value if hasattr(filters.sort, "value") else filters.sort,
    )

    # Expose total count in headers (front‑end uses X-Total)
    if response is not None:
        response.headers["X-Total"] = str(total)

    return [EventCard.from_orm(e) for e in events]


# ----------------------------------------------------------------------------
# DETAIL
# ----------------------------------------------------------------------------


@router.get("/{event_id}", response_model=EventDetail)
def get_event(event_id: str, session: Session = Depends(db_session)):
    event = crud_get_event(session, event_id)
    if not event:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Event not found")
    return EventDetail.from_orm(event)


# ----------------------------------------------------------------------------
# CREATE
# ----------------------------------------------------------------------------


@router.post("/", response_model=EventDetail, status_code=status.HTTP_201_CREATED)
def create_event(
    payload: EventCreate,
    session: Session = Depends(db_session),
):
    event = crud_create_event(session, **payload.dict(exclude={"slots"}), slots=payload.slots)
    return EventDetail.from_orm(event)


# ----------------------------------------------------------------------------
# UPDATE (PATCH)
# ----------------------------------------------------------------------------


@router.patch("/{event_id}", response_model=EventDetail)
def update_event(
    event_id: str,
    payload: EventUpdate,
    session: Session = Depends(db_session),
):
    event = crud_get_event(session, event_id)
    if not event:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Event not found")

    event = crud_update_event(session, event, **payload.dict(exclude_none=True))
    return EventDetail.from_orm(event)


# ----------------------------------------------------------------------------
# DELETE (optional – could be admin‑only)
# ----------------------------------------------------------------------------


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_event(event_id: str, session: Session = Depends(db_session)):
    event = crud_get_event(session, event_id)
    if not event:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Event not found")
    crud_delete_event(session, event)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# ----------------------------------------------------------------------------
# PRESIGNED IMAGE UPLOAD URL
# ----------------------------------------------------------------------------


@router.post("/{event_id}/image-url")
def get_image_upload_url(
    event_id: str,
    session: Session = Depends(db_session),
):
    """Returns presigned PUT URL + public GET URL for branding image."""

    if generate_event_image_urls is None:
        raise HTTPException(
            status.HTTP_501_NOT_IMPLEMENTED,
            detail="Presign service not configured",
        )

    event = crud_get_event(session, event_id)
    if not event:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Event not found")

    upload_url, public_url = generate_event_image_urls(event_id)
    return {"upload_url": upload_url, "public_url": public_url}
