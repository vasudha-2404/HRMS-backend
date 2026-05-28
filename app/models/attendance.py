"""Attendance tracking model."""

import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Date, DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import BaseModel
from app.utils.enums import AttendanceStatus

if TYPE_CHECKING:
    from app.models.employee import Employee


class Attendance(BaseModel, Base):
    __tablename__ = "attendance"

    employee_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("employees.id"), nullable=False, index=True
    )
    attendance_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    check_in: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    check_out: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    check_in_latitude: Mapped[Decimal | None] = mapped_column(Numeric(10, 7), nullable=True)
    check_in_longitude: Mapped[Decimal | None] = mapped_column(Numeric(10, 7), nullable=True)
    check_out_latitude: Mapped[Decimal | None] = mapped_column(Numeric(10, 7), nullable=True)
    check_out_longitude: Mapped[Decimal | None] = mapped_column(Numeric(10, 7), nullable=True)
    total_hours: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    status: Mapped[str] = mapped_column(
        String(30), default=AttendanceStatus.PRESENT.value, nullable=False
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_approved: Mapped[bool] = mapped_column(default=False, nullable=False)
    approved_by_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("employees.id"), nullable=True
    )

    employee: Mapped["Employee"] = relationship(
        "Employee", back_populates="attendances", foreign_keys=[employee_id]
    )
    approved_by: Mapped[Optional["Employee"]] = relationship(
        "Employee", foreign_keys=[approved_by_id]
    )
