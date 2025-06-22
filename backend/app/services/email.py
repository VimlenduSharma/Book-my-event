"""
Outbound e-mail helpers
=======================

Called from Celery tasks or directly (e.g. password-less login links).

Core API
--------
send_email_plain(
    to: str,
    subject: str,
    body: str,
    *,
    reply_to: str | None = None,
    cc: list[str] | None = None,
    bcc: list[str] | None = None,
)
"""

from __future__ import annotations

import logging
import textwrap
from typing import Iterable, List, Sequence

import httpx

from app.core.config import settings

try:
    import boto3
    from botocore.exceptions import BotoCoreError, ClientError
except ModuleNotFoundError:  # pragma: no cover
    boto3 = None  # type: ignore

log = logging.getLogger(__name__)

# ──────────────────────────────────────────────────────────────────────
# Public façade
# ──────────────────────────────────────────────────────────────────────


def send_email_plain(
    *,
    to: str | Sequence[str],
    subject: str,
    body: str,
    reply_to: str | None = None,
    cc: Sequence[str] | None = None,
    bcc: Sequence[str] | None = None,
) -> None:
    """
    Dispatches the message to the backend chosen in `.env`.

    Never raises on network errors – logs them instead so the calling
    service doesn’t explode.
    """
    backend = settings.EMAIL_BACKEND.lower()

    if isinstance(to, str):
        to = [to]

    if backend == "console":
        _send_console(to, subject, body)
    elif backend == "ses":
        _send_ses(to, subject, body, reply_to, cc, bcc)
    elif backend == "sendgrid":
        _send_sendgrid(to, subject, body, reply_to, cc, bcc)
    else:  # pragma: no cover
        log.warning("Unknown EMAIL_BACKEND %s → falling back to console", backend)
        _send_console(to, subject, body)


# ──────────────────────────────────────────────────────────────────────
# Concrete back-ends
# ──────────────────────────────────────────────────────────────────────


def _send_console(to: Iterable[str], subject: str, body: str) -> None:
    log.info(
        "\n==== Console e-mail ====\nTo: %s\nSubj: %s\n\n%s\n========================",
        ", ".join(to),
        subject,
        textwrap.indent(body, "│ "),
    )


# ——— AWS SES ————————————————————————————————————————————————


def _send_ses(
    to: Sequence[str],
    subject: str,
    body: str,
    reply_to: str | None,
    cc: Sequence[str] | None,
    bcc: Sequence[str] | None,
) -> None:
    if boto3 is None:  # pragma: no cover
        log.error("boto3 not installed – cannot send via SES")
        return

    try:
        ses = boto3.client("ses", region_name=settings.SES_REGION)
        ses.send_email(
            Source=settings.EMAIL_FROM,
            Destination={
                "ToAddresses": list(to),
                "CcAddresses": list(cc or []),
                "BccAddresses": list(bcc or []),
            },
            Message={
                "Subject": {"Data": subject, "Charset": "UTF-8"},
                "Body": {"Text": {"Data": body, "Charset": "UTF-8"}},
            },
            ReplyToAddresses=[reply_to] if reply_to else [],
        )
        log.debug("SES e-mail sent to %s", to)
    except (BotoCoreError, ClientError) as exc:  # pragma: no cover
        log.exception("SES send_email failed: %s", exc)


# ——— SendGrid (thin HTTP client, no heavy SDK) ————————————————


def _send_sendgrid(
    to: Sequence[str],
    subject: str,
    body: str,
    reply_to: str | None,
    cc: Sequence[str] | None,
    bcc: Sequence[str] | None,
) -> None:
    if not settings.SENDGRID_API_KEY:
        log.error("SENDGRID_API_KEY missing – cannot send mail")
        return

    api_url = "https://api.sendgrid.com/v3/mail/send"
    headers = {
        "Authorization": f"Bearer {settings.SENDGRID_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "personalizations": [
            {
                "to": [{"email": addr} for addr in to],
                "cc": [{"email": addr} for addr in (cc or [])] or None,
                "bcc": [{"email": addr} for addr in (bcc or [])] or None,
            }
        ],
        "from": {"email": settings.EMAIL_FROM},
        "subject": subject,
        "content": [{"type": "text/plain", "value": body}],
    }
    if reply_to:
        payload["reply_to"] = {"email": reply_to}

    # Remove None keys the API dislikes
    payload = {k: v for k, v in payload.items() if v is not None}

    try:
        resp = httpx.post(api_url, json=payload, headers=headers, timeout=10)
        if resp.status_code >= 400:  # pragma: no cover
            log.error("SendGrid error %s – %s", resp.status_code, resp.text)
        else:
            log.debug("SendGrid e-mail accepted for %s", to)
    except Exception:  # pragma: no cover
        log.exception("SendGrid HTTP call failed")
