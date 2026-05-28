"""Recruitment ATS schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from app.schemas.common import TimestampSchema


class JobOpeningCreate(BaseModel):
    title: str
    description: str
    department: str | None = None
    location: str | None = None
    employment_type: str = "full_time"
    vacancies: int = 1
    salary_range: str | None = None


class JobOpeningResponse(TimestampSchema):
    title: str
    description: str
    department: str | None
    location: str | None
    employment_type: str
    vacancies: int
    is_active: bool


class ApplicantCreate(BaseModel):
    full_name: str
    email: EmailStr
    phone: str | None = None
    resume_url: str | None = None
    job_opening_id: UUID
    source: str | None = None


class ApplicantStageUpdate(BaseModel):
    stage: str
    notes: str | None = None
    rating: int | None = Field(default=None, ge=1, le=5)


class ApplicantResponse(TimestampSchema):
    full_name: str
    email: str
    phone: str | None
    stage: str
    job_opening_id: UUID
    rating: int | None = None


class InterviewCreate(BaseModel):
    applicant_id: UUID
    scheduled_at: datetime
    duration_minutes: int = 60
    interview_type: str = "technical"
    location: str | None = None
    meeting_link: str | None = None
    interviewer_id: UUID | None = None


class InterviewFeedback(BaseModel):
    feedback: str
    rating: int = Field(ge=1, le=5)
    status: str = "completed"


class InterviewResponse(TimestampSchema):
    applicant_id: UUID
    scheduled_at: datetime
    duration_minutes: int
    interview_type: str
    status: str
    feedback: str | None = None
    rating: int | None = None
