from __future__ import annotations

"""Application entry‑point (FastAPI instance)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
All domain routers, middleware, and startup hooks are wired here.
"""

import logging
from pathlib import Path
from typing import List

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core import settings
from app.core.database import init_db
from app.api.v1 import reviews_router
from app.api.v1 import meta_router


# ────────────────────────────────────────────────────────────────
# FastAPI app instance
# ────────────────────────────────────────────────────────────────

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    debug=settings.DEBUG,
)

# ────────────────────────────────────────────────────────────────
# CORS (origins pulled from .env)
# ────────────────────────────────────────────────────────────────

allow_origins: List[str] = [str(o) for o in settings.BACKEND_CORS_ORIGINS]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ────────────────────────────────────────────────────────────────
# Routers – keep import *after* app to avoid circular refs
# ────────────────────────────────────────────────────────────────

from app.api.v1 import events_router, bookings_router  # noqa: E402
from app.api import ws_router  # noqa: E402

app.include_router(events_router)
app.include_router(bookings_router)
app.include_router(ws_router)
app.include_router(reviews_router)
app.include_router(meta_router)

# Future: meta_router, reviews_router, etc.

# ────────────────────────────────────────────────────────────────
# Health‑check & root redirect helpers
# ────────────────────────────────────────────────────────────────


@app.get("/health", tags=["meta"])
def health() -> dict[str, str]:
    """Simple liveness probe for k8s / Render."""
    return {"status": "ok"}


@app.get("/", include_in_schema=False)
def root() -> dict[str, str]:
    """Friendly root endpoint links to docs."""
    return {"docs": "/docs", "redoc": "/redoc"}


# ────────────────────────────────────────────────────────────────
# Startup (dev DB init + banner)
# ────────────────────────────────────────────────────────────────


@app.on_event("startup")
def _startup() -> None:  # noqa: D401
    logging.getLogger(__name__).info("🚀  %s starting in %s mode", settings.APP_NAME, settings.APP_ENV)

    # Auto‑create tables in dev/test (prod uses Alembic)
    if settings.APP_ENV in {"dev", "test"}:
        init_db()

    # Write a .gitignore'd banner so Dockerfile's healthcheck can ping it
    Path("/tmp/app_started").touch(exist_ok=True)
