"""Task and report models."""

import uuid
from datetime import date, datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Date, DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import BaseModel
from app.utils.enums import TaskPriority, TaskStatus

if TYPE_CHECKING:
    from app.models.employee import Employee
    from app.models.project import Project
    from app.models.user import User


class Task(BaseModel, Base):
    __tablename__ = "tasks"

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[TaskStatus] = mapped_column(
        Enum(
            TaskStatus,
            name="task_status_enum",
            create_type=False,
            values_callable=lambda enum: [e.value for e in enum],
        ),
        default=TaskStatus.TODO,
        nullable=False,
    )
    priority: Mapped[TaskPriority] = mapped_column(
        Enum(
            TaskPriority,
            name="task_priority_enum",
            create_type=False,
            values_callable=lambda enum: [e.value for e in enum],
        ),
        default=TaskPriority.MEDIUM,
        nullable=False,
    )
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    assignee_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("employees.id"), nullable=True
    )
    assigned_by_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("employees.id"), nullable=True
    )
    project_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id"), nullable=True
    )

    assignee: Mapped[Optional["Employee"]] = relationship(
        "Employee", back_populates="assigned_tasks", foreign_keys=[assignee_id]
    )
    assigned_by: Mapped[Optional["Employee"]] = relationship(
        "Employee", foreign_keys=[assigned_by_id]
    )
    project: Mapped[Optional["Project"]] = relationship("Project", back_populates="tasks")
    comments: Mapped[List["TaskComment"]] = relationship(
        "TaskComment", back_populates="task", cascade="all, delete-orphan"
    )


class TaskComment(BaseModel, Base):
    __tablename__ = "task_comments"

    task_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tasks.id"), nullable=False
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)

    task: Mapped["Task"] = relationship("Task", back_populates="comments")
    user: Mapped["User"] = relationship("User")


class Report(BaseModel, Base):
    __tablename__ = "reports"

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    report_type: Mapped[str] = mapped_column(String(50), nullable=False)
    report_date: Mapped[date] = mapped_column(Date, nullable=False)

    employee_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("employees.id"), nullable=False
    )
    project_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id"), nullable=True
    )

    employee: Mapped["Employee"] = relationship("Employee")
    project: Mapped[Optional["Project"]] = relationship("Project")
