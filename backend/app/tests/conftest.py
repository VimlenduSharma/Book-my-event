"""conftest.py – Global pytest fixtures for the Scheduler back‑end
================================================================
These fixtures wire up an **in‑memory SQLite database**, dependency
overrides, an event‑loop for async tests, and a TestClient that runs
all Celery tasks **eagerly** so you don’t need a worker during unit
runs.
"""

from __future__ import annotations

import asyncio
import os
from typing import AsyncGenerator, Generator, Tuple

import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session, create_engine

# ────────────────────────────────────────────────────────────────
# Import application objects *after* any environment tweaks
# ────────────────────────────────────────────────────────────────

# Ensure a clean env before settings are imported
os.environ.setdefault("APP_ENV", "test")

from app.core.config import settings  # noqa: E402
from app.core.celery_app import celery_app  # noqa: E402
from app.main import app  # noqa: E402
from app.api.deps import db_session as _db_session  # noqa: E402

# ────────────────────────────────────────────────────────────────
# Asyncio event loop – module scope so async tests share it
# ────────────────────────────────────────────────────────────────


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:  # type: ignore[name-defined]
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


# ────────────────────────────────────────────────────────────────
# Database: in‑memory SQLite (one per test session)
# ────────────────────────────────────────────────────────────────


def _build_test_engine():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        echo=False,
    )
    return engine


@pytest.fixture(scope="session")
def engine():
    """Singleton SQLModel engine for the whole test run."""
    engine_obj = _build_test_engine()

    # Import models once so metadata is populated
    import app.models  # noqa: F401 – side‑effect import

    SQLModel.metadata.create_all(engine_obj)
    yield engine_obj
    SQLModel.metadata.drop_all(engine_obj)


@pytest.fixture
def session(engine) -> Generator[Session, None, None]:
    """Create a *rollback‑after* Session for each test function."""

    with Session(engine) as s:
        # BEGIN a nested transaction
        trans = s.begin_nested()
        yield s
        # Rollback to savepoint → clean state
        trans.rollback()
        # Expire objects so subsequent tests don’t see stale state
        s.expunge_all()


# ────────────────────────────────────────────────────────────────
# Dependency override – FastAPI gets the Session above
# ────────────────────────────────────────────────────────────────


def _override_db_session() -> Generator[Session, None, None]:
    from contextlib import contextmanager

    @contextmanager
    def _ctx() -> Generator[Session, None, None]:
        with Session(engine) as s:  # type: ignore[arg-type]
            trans = s.begin_nested()
            try:
                yield s
                trans.commit()
            finally:
                s.expunge_all()
    yield from _ctx()


app.dependency_overrides[_db_session] = _override_db_session  # type: ignore[assignment]


# ────────────────────────────────────────────────────────────────
# Celery – run tasks eagerly during tests
# ────────────────────────────────────────────────────────────────

celery_app.conf.task_always_eager = True
celery_app.conf.task_eager_propagates = True


# ────────────────────────────────────────────────────────────────
# HTTP client
# ────────────────────────────────────────────────────────────────


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    """FastAPI TestClient with DB + Celery overrides already applied."""
    with TestClient(app) as c:
        yield c
