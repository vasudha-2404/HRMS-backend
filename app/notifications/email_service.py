"""Email notification service (architecture-ready for SMTP)."""

import logging
from typing import Any

from app.core.config import settings

logger = logging.getLogger("pathvision.email")


class EmailService:
    """Placeholder email service - wire SMTP in production."""

    async def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        html: bool = False,
    ) -> bool:
        if not settings.SMTP_HOST:
            logger.info("Email queued (SMTP not configured): to=%s subject=%s", to, subject)
            return True

        # Production: implement aiosmtplib or Celery task
        logger.info("Sending email to %s: %s", to, subject)
        return True

    async def send_leave_notification(self, to: str, leave_data: dict[str, Any]) -> bool:
        subject = f"Leave Request - {leave_data.get('status', 'update')}"
        body = f"Your leave request from {leave_data.get('start_date')} has been updated."
        return await self.send_email(to, subject, body)

    async def send_task_assignment(self, to: str, task_title: str) -> bool:
        return await self.send_email(to, f"New Task: {task_title}", f"You have been assigned: {task_title}")
