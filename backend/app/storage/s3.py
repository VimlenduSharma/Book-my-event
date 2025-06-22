"""
Typed helper for obtaining a boto3 S3 client and building public URLs.

All configuration values come from `app.core.config.settings`.
"""

from __future__ import annotations

import uuid
from typing import Optional

import boto3
from botocore.client import Config  # noqa: WPS433 (runtime import)

from app.core.config import settings


def get_s3_client():
    """
    Return a boto3 S3 **client** configured for MinIO or AWS.

    • Works with both traditional AWS endpoint **and** local MinIO.
    • Reuses credentials from `.env` via settings.
    """
    return boto3.client(
        "s3",
        endpoint_url=settings.S3_ENDPOINT_URL or None,
        aws_access_key_id=settings.S3_ACCESS_KEY,
        aws_secret_access_key=settings.S3_SECRET_KEY,
        config=Config(signature_version="s3v4"),
    )


def get_public_url(key: str) -> str:
    """
    Build the final public GET URL for an object `key`.

    * If `S3_ENDPOINT_URL` is defined (MinIO, custom domain) -> use it
    * Else fall back to the standard `https://{bucket}.s3.amazonaws.com/{key}`
    """
    if settings.S3_ENDPOINT_URL:
        return f"{settings.S3_ENDPOINT_URL.rstrip('/')}/{settings.S3_BUCKET}/{key}"
    return f"https://{settings.S3_BUCKET}.s3.amazonaws.com/{key}"


def random_key(prefix: str, ext: str) -> str:
    """
    Produce a unique object key like `images/<uuid>.png`.
    """
    return f"{prefix}/{uuid.uuid4().hex}.{ext.lstrip('.')}"
