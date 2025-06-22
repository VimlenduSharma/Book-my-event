"""
Database layer (SQLModel + SQLAlchemy)

This module exposes:

* `engine` – singleton SQLAlchemy Engine
* `SessionLocal` – sessionmaker factory
* `get_session()` – context-managed generator for anywhere in the codebase
* `init_db()` – create tables on first run (dev convenience)

It stays **framework-agnostic**: no FastAPI imports, so Celery
workers or Alembic migrations can use it as-is.
"""

from __future__ import annotations

import logging
from contextlib import contextmanager
from typing import Generator

from sqlalchemy.orm import sessionmaker
from sqlmodel import Session, SQLModel, create_engine

from app.core.config import settings

log = logging.getLogger(__name__)

# ————————————————————————————————————————————————————————————————
# Engine
# ————————————————————————————————————————————————————————————————

# SQLite needs a special flag for multi-thread dev servers
_connect_args: dict = {}
if str(settings.DATABASE_URL).startswith("sqlite"):
    _connect_args["check_same_thread"] = False

engine = create_engine(
    str(settings.DATABASE_URL),
    echo=settings.DEBUG,            # SQL echo in dev
    future=True,                    # SQLAlchemy 2.x style
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    connect_args=_connect_args,
)

# ————————————————————————————————————————————————————————————————
# Session factory
# ————————————————————————————————————————————————————————————————

SessionLocal: sessionmaker[Session] = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=Session,
    expire_on_commit=False,
)


# ————————————————————————————————————————————————————————————————
# Helper: create tables (DEV only)
# ————————————————————————————————————————————————————————————————

def init_db() -> None:
    """
    Import all model modules **once** and create tables.

    Call this from a FastAPI startup event *only in dev*;
    prod environments should rely on Alembic migrations.
    """
    import app.models  # noqa: F401 – side-effect import
    SQLModel.metadata.create_all(bind=engine)
    log.info("📦  Database schema ensured")


# ————————————————————————————————————————————————————————————————
# Context-managed session (usable everywhere)
# ————————————————————————————————————————————————————————————————

@contextmanager
def get_session() -> Generator[Session, None, None]:
    """
    Yields a SQLModel `Session` with commit / rollback safety.

    Example
    -------
    >>> with get_session() as session:
    ...     users = session.exec(select(User)).all()
    """
    session: Session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:  # noqa: BLE001
        session.rollback()
        raise
    finally:
        session.close()
