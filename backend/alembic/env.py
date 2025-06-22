"""alembic/env.py – Alembic environment script
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This script is executed by Alembic’s `upgrade`, `downgrade`, `revision`, etc.
It wires **SQLModel / SQLAlchemy 2** metadata into the migration context,
loads settings from the application, and supports both *offline* and
*online* migration modes.
"""
from __future__ import annotations

import asyncio
import logging
import sys
from pathlib import Path
from typing import Sequence

from alembic import context
from sqlalchemy import Engine, pool
from sqlmodel import SQLModel, create_engine

# ---------------------------------------------------------------
# Ensure app is importable (repo root added to PYTHONPATH)
# ---------------------------------------------------------------

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Now we can import settings and models
from app.core.config import settings  # noqa: E402  (import after sys.path tweak)
import app.models  # noqa: F401 – side‑effect populates SQLModel.metadata

logger = logging.getLogger("alembic.env")

# ---------------------------------------------------------------
# Target metadata for 'autogenerate'
# ---------------------------------------------------------------

target_metadata = SQLModel.metadata

# ---------------------------------------------------------------
# Helper: run migrations in *offline* mode (emit SQL)
# ---------------------------------------------------------------

def run_migrations_offline() -> None:
    """Run migrations without a DB connection (generates SQL scripts)."""
    url = str(settings.DATABASE_URL)
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )
    with context.begin_transaction():
        context.run_migrations()


# ---------------------------------------------------------------
# Helper: run migrations *online* (apply to DB)
# ---------------------------------------------------------------

def _run_migrations(engine: Engine) -> None:
    connectable = engine

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )
        with context.begin_transaction():
            context.run_migrations()


def run_migrations_online() -> None:  # noqa: D401
    """Run migrations in online mode (requires DB connection)."""

    connect_args = {}
    if str(settings.DATABASE_URL).startswith("sqlite"):
        connect_args["check_same_thread"] = False

    engine = create_engine(
        str(settings.DATABASE_URL),
        poolclass=pool.NullPool,
        connect_args=connect_args,
        future=True,
    )

    if context.is_async_mode():
        # Asyncio engines (not used here but Alembic may invoke)
        async def _run_async_migrations() -> None:  # pragma: no cover
            async with engine.begin() as conn:  # type: ignore[attr-defined]
                await conn.run_sync(_run_migrations)  # type: ignore[arg-type]
        asyncio.run(_run_async_migrations())
    else:
        _run_migrations(engine)


# ---------------------------------------------------------------
# Entry‑point Alembic calls
# ---------------------------------------------------------------

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
