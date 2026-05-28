"""Employee management model."""

import uuid
from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Date, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import BaseModel
from app.utils.enums import EmploymentStatus

if TYPE_CHECKING:
    from app.models.attendance import Attendance
    from app.models.department import Department, Team
    from app.models.leave import Leave
    from app.models.task import Task
    from app.models.user import User


class Employee(BaseModel, Base):
    __tablename__ = "employees"

    employee_code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    designation: Mapped[str] = mapped_column(String(100), nullable=False)
    date_of_joining: Mapped[date] = mapped_column(Date, nullable=False)
    date_of_birth: Mapped[date | None] = mapped_column(Date, nullable=True)
    gender: Mapped[str | None] = mapped_column(String(20), nullable=True)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    emergency_contact: Mapped[str | None] = mapped_column(String(50), nullable=True)
    employment_status: Mapped[str] = mapped_column(
        String(30), default=EmploymentStatus.ACTIVE.value, nullable=False
    )
    salary: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), unique=True, nullable=False
    )
    department_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("departments.id"), nullable=True
    )
    team_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("teams.id"), nullable=True
    )
    manager_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("employees.id"), nullable=True
    )

    user: Mapped["User"] = relationship("User", back_populates="employee")
    department: Mapped[Optional["Department"]] = relationship(
        "Department", back_populates="employees", foreign_keys=[department_id]
    )
    team: Mapped[Optional["Team"]] = relationship(
        "Team", back_populates="employees", foreign_keys=[team_id]
    )
    manager: Mapped[Optional["Employee"]] = relationship(
        "Employee", remote_side="Employee.id", foreign_keys=[manager_id]
    )
    attendances: Mapped[List["Attendance"]] = relationship(
        "Attendance", back_populates="employee", foreign_keys="Attendance.employee_id"
    )
    leaves: Mapped[List["Leave"]] = relationship("Leave", back_populates="employee")
    assigned_tasks: Mapped[List["Task"]] = relationship(
        "Task", back_populates="assignee", foreign_keys="Task.assignee_id"
    )
