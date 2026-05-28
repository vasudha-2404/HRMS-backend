"""Notification schemas."""

from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.common import TimestampSchema


class NotificationCreate(BaseModel):
    user_id: UUID
    title: str
    message: str
    notification_type: str = "info"
    priority: str = "medium"
    action_url: str | None = None


class NotificationResponse(TimestampSchema):
    user_id: UUID
    title: str
    message: str
    notification_type: str
    priority: str
    is_read: bool
    action_url: str | None = None
