"""
Celery application factory.

* Broker  : Redis  ➟  settings.REDIS_URL
* Backend : Redis  (can be swapped for DB/S3)
* Task auto-discovery under  app/workers/*
* Optional Beat scheduler for FX-rate refresh

Import this module ONCE in each process:

    from app.core.celery_app import celery_app
"""

from __future__ import annotations

import logging
from datetime import timedelta
from typing import Sequence

from celery import Celery
from kombu import Exchange, Queue

from app.core.config import settings

log = logging.getLogger(__name__)

# ————————————————————————————————————————————————————————————————
# 1. Instantiate
# ————————————————————————————————————————————————————————————————

celery_app = Celery(
    "scheduler",                       # app name
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=[                          # explicit import fallback
        "app.workers.email",
        "app.workers.calendar",
        "app.workers.fx",
    ],
)

# ————————————————————————————————————————————————————————————————
# 2. Global configuration
# ————————————————————————————————————————————————————————————————

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    worker_prefetch_multiplier=1,      # fair scheduling
)

# ————————————————————————————————————————————————————————————————
# 3. Queues / Routing (optional but tidy)
# ————————————————————————————————————————————————————————————————

default_exchange = Exchange("default", type="direct")

celery_app.conf.task_queues: Sequence[Queue] = (
    Queue("default",   default_exchange, routing_key="default"),
    Queue("emails",    Exchange("emails"),   routing_key="emails"),
    Queue("analytics", Exchange("analytics"), routing_key="analytics"),
)

celery_app.conf.task_default_queue = "default"
celery_app.conf.task_default_exchange = "default"
celery_app.conf.task_default_routing_key = "default"

# Example router (extend as needed)
celery_app.conf.task_routes = {
    "app.workers.email.*":     {"queue": "emails"},
    "app.workers.fx.*":        {"queue": "analytics"},
}

# ————————————————————————————————————————————————————————————————
# 4. Beat schedule (FX-rate refresh every N hours)
# ————————————————————————————————————————————————————————————————

celery_app.conf.beat_schedule = {
    "refresh-fx-rates": {
        "task": "app.workers.fx.refresh_rates",
        "schedule": timedelta(hours=settings.FX_REFRESH_HOURS),
        "options": {"queue": "analytics"},
    },
}

# ————————————————————————————————————————————————————————————————
# 5. Health task (good for k8s probes)
# ————————————————————————————————————————————————————————————————

@celery_app.task(name="health.ping")
def ping() -> str:  # noqa: D401
    """Simple ping task to verify worker connectivity."""
    log.debug("↪️  Celery ping received")
    return "pong"
