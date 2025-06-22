from __future__ import annotations

"""tests/test_events.py – high‑level API tests for Event endpoints"""

from datetime import datetime, timezone
from typing import Dict, Any

import pytest
from fastapi.testclient import TestClient

ISO = "%Y-%m-%dT%H:%M:%SZ"


def _event_payload() -> Dict[str, Any]:
    """Return a fully‑formed JSON payload for POST /events"""
    start_time = datetime(2030, 1, 1, 10, 0, tzinfo=timezone.utc).strftime(ISO)
    return {
        "title": "Design Sprint",
        "description": "Rapid prototyping session",
        "host_name": "Alice",
        "category": "Design",
        "duration_min": 90,
        "price_minor": 4500,
        "currency": "USD",
        "timezone": "America/New_York",
        "image_url": None,
        "slots": [
            {"start_utc": start_time, "max_bookings": 3}
        ],
    }


@pytest.fixture
def created_event(client: TestClient) -> dict:
    """Create an event and return the response JSON."""
    resp = client.post("/events", json=_event_payload())
    assert resp.status_code == 201
    return resp.json()


# ---------------------------------------------------------------------------
# CREATE & DETAIL
# ---------------------------------------------------------------------------


def test_create_event_and_get_detail(client: TestClient):
    payload = _event_payload()
    create_resp = client.post("/events", json=payload)
    assert create_resp.status_code == 201
    data = create_resp.json()

    # basic shape
    assert data["title"] == payload["title"]
    assert data["remaining_slots"] == 1  # one slot object
    assert len(data["slots"]) == 1
    slot = data["slots"][0]
    assert slot["remaining"] == payload["slots"][0]["max_bookings"]

    # GET detail should match
    evt_id = data["id"]
    detail_resp = client.get(f"/events/{evt_id}")
    assert detail_resp.status_code == 200
    assert detail_resp.json()["id"] == evt_id


# ---------------------------------------------------------------------------
# LIST & FILTERS
# ---------------------------------------------------------------------------


def test_list_events_returns_x_total_header(client: TestClient, created_event):
    resp = client.get("/events")
    assert resp.status_code == 200
    assert resp.headers.get("X-Total") == "1"
    assert len(resp.json()) == 1


# ensure category filter works

def test_list_events_filter_category(client: TestClient, created_event):
    resp = client.get("/events", params={"category": "Business"})
    assert resp.status_code == 200
    # no business events yet
    assert resp.json() == []


# ---------------------------------------------------------------------------
# PATCH & DELETE
# ---------------------------------------------------------------------------


def test_patch_then_delete_event(client: TestClient, created_event):
    evt_id = created_event["id"]

    # Patch title
    patch_resp = client.patch(f"/events/{evt_id}", json={"title": "UX Workshop"})
    assert patch_resp.status_code == 200
    assert patch_resp.json()["title"] == "UX Workshop"

    # Delete
    del_resp = client.delete(f"/events/{evt_id}")
    assert del_resp.status_code == 204

    # Ensure gone
    missed = client.get(f"/events/{evt_id}")
    assert missed.status_code == 404
