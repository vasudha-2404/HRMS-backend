"""Celery application for background tasks."""

from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "pathvision_hrms",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
)


@celery_app.task(name="send_notification_email")
def send_notification_email(to: str, subject: str, body: str) -> bool:
    """Background task for email notifications."""
    import logging

    logging.getLogger("pathvision.celery").info("Email task: %s -> %s", to, subject)
    return True
