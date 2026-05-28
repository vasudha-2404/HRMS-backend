"""Task schemas."""

from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.common import TimestampSchema


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = None
    priority: str = "medium"
    due_date: date | None = None
    assignee_id: UUID | None = None
    project_id: UUID | None = None


class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    status: str | None = None
    priority: str | None = None
    due_date: date | None = None
    assignee_id: UUID | None = None


class TaskCommentCreate(BaseModel):
    content: str = Field(min_length=1)


class TaskResponse(TimestampSchema):
    title: str
    description: str | None
    status: str
    priority: str
    due_date: date | None
    assignee_id: UUID | None
    assigned_by_id: UUID | None
    project_id: UUID | None
    completed_at: datetime | None = None


class TaskCommentResponse(TimestampSchema):
    task_id: UUID
    user_id: UUID
    content: str
