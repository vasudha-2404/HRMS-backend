"""Department and team organizational models."""

import uuid
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.employee import Employee
    from app.models.project import Project


class Department(BaseModel, Base):
    __tablename__ = "departments"

    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    head_employee_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("employees.id", use_alter=True), nullable=True
    )

    teams: Mapped[List["Team"]] = relationship("Team", back_populates="department")
    employees: Mapped[List["Employee"]] = relationship(
        "Employee",
        back_populates="department",
        foreign_keys="Employee.department_id",
    )
    projects: Mapped[List["Project"]] = relationship("Project", back_populates="department")


class Team(BaseModel, Base):
    __tablename__ = "teams"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    department_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("departments.id"), nullable=False
    )
    lead_employee_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("employees.id", use_alter=True), nullable=True
    )

    department: Mapped["Department"] = relationship("Department", back_populates="teams")
    employees: Mapped[List["Employee"]] = relationship(
        "Employee", back_populates="team", foreign_keys="Employee.team_id"
    )
