"""
Common FastAPI dependencies
===========================

Routers import helpers from this module instead of re-writing the
same boilerplate over and over.

* ``db_session``      – SQLModel session (transaction scope)
* ``current_email``   – Optional e-mail extracted from header *or* query
* ``required_email``  – Same but raises 400 if missing
* ``pagination``      – Validated (page, size) tuple

Usage
-----
    from app.api.deps import db_session, required_email, pagination
"""

from __future__ import annotations

from typing import Generator, Tuple

from fastapi import Depends, Header, HTTPException, Query, status
from pydantic import EmailStr
from sqlmodel import Session

from app.core.database import get_session

# ————————————————————————————————————————————————————————————————
# Database session
# ————————————————————————————————————————————————————————————————


def db_session() -> Generator[Session, None, None]:
    """
    Yields a SQLModel Session inside a transaction scope.
    """
    with get_session() as session:
        yield session


# ————————————————————————————————————————————————————————————————
# Lightweight “identity” (e-mail) helpers
# ————————————————————————————————————————————————————————————————


def current_email(
    x_user_email: str | None = Header(
        None,
        alias="X-User-Email",
        description="Visitor’s e-mail; front-end sets this header when known.",
    ),
    email_query: str | None = Query(
        None,
        alias="email",
        description="Fallback ?email= query parameter.",
    ),
) -> EmailStr | None:
    """
    Returns a *validated* e-mail string **or** ``None`` if not supplied.

    Routers that *require* identity should depend on
    ``required_email`` instead.
    """
    email_value = x_user_email or email_query
    return EmailStr(email_value) if email_value else None


def required_email(email: EmailStr | None = Depends(current_email)) -> EmailStr:
    """
    Same as ``current_email`` but raises **400** if not present.
    """
    if email is None:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail="E-mail identity required for this operation.",
        )
    return email


# ————————————————————————————————————————————————————————————————
# Pagination helper
# ————————————————————————————————————————————————————————————————

DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100


def pagination(
    page: int = Query(1, ge=1, description="Page number (starts at 1)"),
    size: int = Query(
        DEFAULT_PAGE_SIZE,
        ge=1,
        le=MAX_PAGE_SIZE,
        description=f"Items per page (max {MAX_PAGE_SIZE})",
    ),
) -> Tuple[int, int]:
    """
    Returns validated ``(page, size)`` tuple.
    """
    return page, size
