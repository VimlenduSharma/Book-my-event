from app.services.fx import get_rates
from app.core.celery_app import celery_app

@celery_app.task(name="fx.refresh_rates")
def refresh_rates():
    get_rates(force_refresh=True)
