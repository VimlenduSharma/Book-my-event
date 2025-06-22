from __future__ import annotations

"""Foreign‑exchange utility layer
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Fetches daily FX rates from *exchangerate.host* (free & no key) and caches
JSON in Redis so repeated conversions are instant.

Usage (inside FastAPI route):
    from app.services.fx import get_rates, convert_minor

    rates = get_rates()               # base=USD by default
    eur_cents = convert_minor(4500, "USD", "EUR", rates)
"""

import json
import logging
from datetime import timedelta
from typing import Dict, Mapping

import httpx

from app.core.config import settings
from app.core.redis import redis_conn  # global connection from earlier helper

log = logging.getLogger(__name__)

REDIS_KEY = "fx:rates"

# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def get_rates(force_refresh: bool = False) -> Mapping[str, float]:
    """Return dict like `{ 'USD': 1.0, 'EUR': 0.93, … }`.

    Cached in Redis with TTL = `settings.FX_REFRESH_HOURS`.
    """
    if not force_refresh:
        try:
            cached = redis_conn.get(REDIS_KEY)
            if cached:
                return json.loads(cached)
        except Exception:  # pragma: no cover
            log.exception("FX cache read failed")

    rates = _fetch_rates_remote()
    try:
        ttl = settings.FX_REFRESH_HOURS * 3600
        redis_conn.setex(REDIS_KEY, ttl, json.dumps(rates))
    except Exception:  # pragma: no cover
        log.exception("FX cache write failed")

    return rates


def convert_minor(amount_minor: int, from_currency: str, to_currency: str, rates: Mapping[str, float]) -> int:
    """Convert integer *minor* units (cents) using rates dict.

    Rounds to nearest minor unit of target currency.
    """
    if from_currency == to_currency:
        return amount_minor

    try:
        base_ratio = rates[to_currency] / rates[from_currency]
    except KeyError as exc:  # pragma: no cover
        raise ValueError(f"Missing FX rate for {exc.args[0]}") from exc

    return int(round(amount_minor * base_ratio))

# ---------------------------------------------------------------------------
# Internal
# ---------------------------------------------------------------------------

def _fetch_rates_remote() -> Dict[str, float]:
    """Hit exchangerate.host (or custom URL) and return rate dict."""
    try:
        resp = httpx.get(settings.FX_API_URL, params={"base": "USD"}, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        return data["rates"]  # type: ignore[name-defined]
    except Exception as exc:  # pragma: no cover
        log.exception("Failed to fetch FX rates: %s", exc)
        # Fallback to USD 1.0 only – avoids crash, conversions become no‑ops
        return {"USD": 1.0}
