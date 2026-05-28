"""Leave schemas."""

from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.common import TimestampSchema


class LeaveCreate(BaseModel):
    leave_type: str
    start_date: date
    end_date: date
    reason: str = Field(min_length=5)


class LeaveApprovalRequest(BaseModel):
    remarks: str | None = None


class LeaveRejectRequest(BaseModel):
    rejection_reason: str = Field(min_length=5)


class LeaveResponse(TimestampSchema):
    employee_id: UUID
    leave_type: str
    start_date: date
    end_date: date
    total_days: int
    reason: str
    status: str
    team_lead_approved_at: datetime | None = None
    hr_approved_at: datetime | None = None
