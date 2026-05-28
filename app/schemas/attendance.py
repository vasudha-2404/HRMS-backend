"""Attendance schemas."""

from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.common import TimestampSchema


class CheckInRequest(BaseModel):
    latitude: Decimal | None = None
    longitude: Decimal | None = None
    notes: str | None = None


class CheckOutRequest(BaseModel):
    latitude: Decimal | None = None
    longitude: Decimal | None = None
    notes: str | None = None


class AttendanceResponse(TimestampSchema):
    employee_id: UUID
    attendance_date: date
    check_in: datetime | None
    check_out: datetime | None
    total_hours: Decimal | None
    status: str
    is_approved: bool
    check_in_latitude: Decimal | None = None
    check_in_longitude: Decimal | None = None


class AttendanceApprovalRequest(BaseModel):
    is_approved: bool = True
    notes: str | None = None
