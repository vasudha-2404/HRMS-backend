"""Recruitment ATS models."""

import uuid
from datetime import date, datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Date, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import BaseModel
from app.utils.enums import ApplicantStage, EmploymentType, InterviewStatus

if TYPE_CHECKING:
    from app.models.employee import Employee


class JobOpening(BaseModel, Base):
    __tablename__ = "job_openings"

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    department: Mapped[str | None] = mapped_column(String(100), nullable=True)
    location: Mapped[str | None] = mapped_column(String(100), nullable=True)
    employment_type: Mapped[EmploymentType] = mapped_column(
        Enum(
            EmploymentType,
            name="employment_type_enum",
            create_type=False,
            values_callable=lambda enum: [e.value for e in enum],
        ),
        default=EmploymentType.FULL_TIME,
        nullable=False,
    )
    vacancies: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    salary_range: Mapped[str | None] = mapped_column(String(100), nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    posted_by_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("employees.id"), nullable=True
    )

    applicants: Mapped[List["Applicant"]] = relationship(
        "Applicant", back_populates="job_opening"
    )


class Applicant(BaseModel, Base):
    __tablename__ = "applicants"

    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    resume_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    stage: Mapped[ApplicantStage] = mapped_column(
        Enum(
            ApplicantStage,
            name="applicant_stage_enum",
            create_type=False,
            values_callable=lambda enum: [e.value for e in enum],
        ),
        default=ApplicantStage.APPLIED,
        nullable=False,
    )
    source: Mapped[str | None] = mapped_column(String(50), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    rating: Mapped[int | None] = mapped_column(Integer, nullable=True)

    job_opening_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("job_openings.id"), nullable=False
    )

    job_opening: Mapped["JobOpening"] = relationship(
        "JobOpening", back_populates="applicants"
    )
    interviews: Mapped[List["Interview"]] = relationship(
        "Interview", back_populates="applicant", cascade="all, delete-orphan"
    )


class Interview(BaseModel, Base):
    __tablename__ = "interviews"

    applicant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("applicants.id"), nullable=False
    )
    interviewer_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("employees.id"), nullable=True
    )
    scheduled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    duration_minutes: Mapped[int] = mapped_column(Integer, default=60, nullable=False)
    interview_type: Mapped[str] = mapped_column(String(50), default="technical", nullable=False)
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    meeting_link: Mapped[str | None] = mapped_column(String(500), nullable=True)
    feedback: Mapped[str | None] = mapped_column(Text, nullable=True)
    rating: Mapped[int | None] = mapped_column(Integer, nullable=True)
    status: Mapped[InterviewStatus] = mapped_column(
        Enum(
            InterviewStatus,
            name="interview_status_enum",
            create_type=False,
            values_callable=lambda enum: [e.value for e in enum],
        ),
        default=InterviewStatus.SCHEDULED,
        nullable=False,
    )

    applicant: Mapped["Applicant"] = relationship("Applicant", back_populates="interviews")
    interviewer: Mapped[Optional["Employee"]] = relationship("Employee")
