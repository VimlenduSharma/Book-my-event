from __future__ import annotations

"""api/v1/meta.py – Misc helper endpoints
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
* `/categories` → returns canonical list of event categories
* `/fx`         → returns cached FX rates dict
"""

from datetime import datetime, timezone

from fastapi import APIRouter

from app.models.category_enum import CategoryEnum
from app.services.fx import get_rates

router = APIRouter(prefix="", tags=["meta"])


# ---------------------------------------------------------------------------
# /categories – dropdown helper
# ---------------------------------------------------------------------------


@router.get("/categories", response_model=list[str])
def categories():
    """Return all available category strings."""
    return CategoryEnum.list()


# ---------------------------------------------------------------------------
# /fx – cached foreign‑exchange rates
# ---------------------------------------------------------------------------


@router.get("/fx")
def fx_rates():
    """Return cached FX rate map with timestamp."""
    rates = get_rates()
    return {
        "base": "USD",
        "timestamp": datetime.now(tz=timezone.utc).isoformat(),
        "rates": rates,
    }
