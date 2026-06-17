from celery import Celery
from celery.signals import setup_logging

from booking_service.config import settings
from booking_service.logging_config import configure_logging

celery_app = Celery(
    "booking_service",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)
celery_app.conf.task_track_started = True
celery_app.autodiscover_tasks(["booking_service.worker"])


@setup_logging.connect
def _setup_logging(**kwargs):
    configure_logging()
