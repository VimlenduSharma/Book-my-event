"""
Calendar helpers
================

This module converts Booking objects into:

1.  A downloadable *.ics* file (standard iCalendar)
2.  A Google-Calendar “quick-add” link
3.  Helpers for mocked push-sync webhooks (no real OAuth)

The heavy lifting is done with the lightweight *icalendar* library.
"""

from __future__ import annotations

import logging
import tempfile
import urllib.parse
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Literal, Tuple
from uuid import uuid4

try:
    from icalendar import Calendar, Event as ICalEvent
except ModuleNotFoundError:  # pragma: no cover
    raise RuntimeError("pip install icalendar")

from app.core.config import settings
from app.models.booking import Booking

log = logging.getLogger(__name__)

# --------------------------------------------------------------------------------------------------
# Public façade
# --------------------------------------------------------------------------------------------------


def generate_ics_bytes(booking: Booking) -> bytes:
    """
    Convert a Booking row → raw .ics bytes.

    The front-end can `blob:` download or we can persist to S3.
    """

    event = booking.slot.event
    start = booking.slot.start_utc.replace(tzinfo=timezone.utc)
    end = start + timedelta(minutes=event.duration_min)

    cal = Calendar()
    cal.add("prodid", "-//Scheduler//example.com//")
    cal.add("version", "2.0")

    ev = ICalEvent()
    ev.add("uid", f"{booking.id}@scheduler.local")
    ev.add("dtstamp", datetime.utcnow().replace(tzinfo=timezone.utc))
    ev.add("dtstart", start)
    ev.add("dtend", end)
    ev.add("summary", event.title)
    ev.add("description", event.description)
    ev.add("location", "Online")
    ev.add("organizer", f"MAILTO:{settings.EMAIL_FROM}")

    cal.add_component(ev)
    return cal.to_ical()


def write_ics_to_storage(
    booking: Booking,
    *,
    mode: Literal["temp", "s3"] = "temp",
) -> str:
    """
    Store the file and return a **public URL** (or local path for 'temp').

    • **temp** – writes to /tmp, returns `"file:///..."` path \
                 good enough for dev or Vercel functions  
    • **s3**   – uploads to the bucket defined in `.env` \
                 requires `boto3` & credentials (same as images)
    """
    data = generate_ics_bytes(booking)
    filename = f"{booking.id}.ics"

    if mode == "temp":
        path: Path = Path(tempfile.gettempdir()) / filename
        path.write_bytes(data)
        log.debug("ICS written to %s", path)
        return f"file://{path}"
    elif mode == "s3":
        import boto3

        s3 = boto3.client(
            "s3",
            endpoint_url=settings.S3_ENDPOINT_URL or None,
            aws_access_key_id=settings.S3_ACCESS_KEY,
            aws_secret_access_key=settings.S3_SECRET_KEY,
        )
        s3.put_object(
            Bucket=settings.S3_BUCKET,
            Key=f"ics/{filename}",
            Body=data,
            ContentType="text/calendar",
            ACL="public-read",
        )
        url = (
            f"{settings.S3_ENDPOINT_URL}/{settings.S3_BUCKET}/ics/{filename}"
            if settings.S3_ENDPOINT_URL
            else f"https://{settings.S3_BUCKET}.s3.amazonaws.com/ics/{filename}"
        )
        log.debug("ICS uploaded to %s", url)
        return url
    else:  # pragma: no cover
        raise ValueError("mode must be 'temp' or 's3'")


def google_calendar_link(booking: Booking) -> str:
    """
    Build a Google Calendar **quick-add** URL.

    Docs:
    https://developers.google.com/calendar/api/guides/create-events-quickadd
    """
    event = booking.slot.event
    start = booking.slot.start_utc.strftime("%Y%m%dT%H%M%SZ")
    end = (
        booking.slot.start_utc + timedelta(minutes=event.duration_min)
    ).strftime("%Y%m%dT%H%M%SZ")

    query = {
        "action": "TEMPLATE",
        "text": event.title,
        "details": event.description,
        "dates": f"{start}/{end}",
        "location": "Online",
        "trp": "false",
    }
    return f"https://www.google.com/calendar/render?{urllib.parse.urlencode(query)}"


# --------------------------------------------------------------------------------------------------
# Mocked webhook handler (optional)
# --------------------------------------------------------------------------------------------------


def handle_google_webhook(payload: dict) -> None:
    """
    Pretend to parse Google push-sync webhook.

    In real life you’d verify the ID + tokens; here we just log it.
    """
    log.info("🔔  Received calendar webhook: %s", payload)


# --------------------------------------------------------------------------------------------------
# Convenience for Celery tasks
# --------------------------------------------------------------------------------------------------


def upload_ics_and_return_url(booking: Booking) -> str:
    """
    Handy for Celery worker: upload to S3 (if configured) else temp file.
    """
    mode = "s3" if settings.S3_ACCESS_KEY and settings.S3_SECRET_KEY else "temp"
    return write_ics_to_storage(booking, mode=mode)
