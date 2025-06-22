"""
Generate presigned PUT URLs for front-end uploads (brand images, etc.).
"""

from __future__ import annotations

import logging
from typing import Tuple

from app.core.config import settings
from app.storage.s3 import get_public_url, get_s3_client, random_key

log = logging.getLogger(__name__)


def generate_event_image_urls(
    event_id: str,
    *,
    content_type: str = "image/png",
    expire_seconds: int = 3600,
) -> Tuple[str, str]:
    """
    Return **(upload_url, public_url)** for an event branding image.

    Front-end workflow
    ------------------
      1. Call this endpoint (POST `/events/{id}/image-url`).
      2. `PUT` the file directly to `upload_url` with *same* content-type.
      3. Save `public_url` in DB via PATCH `/events/{id}`.

    Parameters
    ----------
    event_id:
        UUID of the parent Event; used to namespace files
    content_type:
        MIME type the browser will send (default png)
    expire_seconds:
        How long the client has to complete the upload
    """
    key = random_key(f"images/{event_id}", ext=content_type.split('/')[-1])
    s3 = get_s3_client()

    try:
        upload_url: str = s3.generate_presigned_url(
            "put_object",
            Params={
                "Bucket": settings.S3_BUCKET,
                "Key": key,
                "ContentType": content_type,
                "ACL": "public-read",
            },
            ExpiresIn=expire_seconds,
        )
        return upload_url, get_public_url(key)
    except Exception:  # pragma: no cover
        log.exception("Failed to create presigned URL")
        raise
