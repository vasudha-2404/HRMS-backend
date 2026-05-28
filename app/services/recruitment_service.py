"""Recruitment ATS service."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.recruitment import Applicant, Interview, JobOpening
from app.schemas.recruitment import (
    ApplicantCreate,
    ApplicantStageUpdate,
    InterviewCreate,
    InterviewFeedback,
    JobOpeningCreate,
)
from app.utils.exceptions import NotFoundException


class RecruitmentService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_job(self, data: JobOpeningCreate, posted_by_id: UUID | None) -> JobOpening:
        job = JobOpening(**data.model_dump(), posted_by_id=posted_by_id)
        self.db.add(job)
        await self.db.flush()
        await self.db.refresh(job)
        return job

    async def list_jobs(self, page: int, page_size: int, active_only: bool = True):
        from sqlalchemy import func

        query = select(JobOpening).where(JobOpening.deleted_at.is_(None))
        if active_only:
            query = query.where(JobOpening.is_active.is_(True))
        total = (
            await self.db.execute(select(func.count()).select_from(query.subquery()))
        ).scalar() or 0
        result = await self.db.execute(
            query.order_by(JobOpening.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        return list(result.scalars().all()), total

    async def create_applicant(self, data: ApplicantCreate) -> Applicant:
        applicant = Applicant(**data.model_dump())
        self.db.add(applicant)
        await self.db.flush()
        await self.db.refresh(applicant)
        return applicant

    async def update_applicant_stage(
        self, applicant_id: UUID, data: ApplicantStageUpdate
    ) -> Applicant:
        result = await self.db.execute(
            select(Applicant).where(
                Applicant.id == applicant_id, Applicant.deleted_at.is_(None)
            )
        )
        applicant = result.scalar_one_or_none()
        if not applicant:
            raise NotFoundException("Applicant")
        applicant.stage = data.stage
        if data.notes:
            applicant.notes = data.notes
        if data.rating:
            applicant.rating = data.rating
        await self.db.flush()
        return applicant

    async def schedule_interview(self, data: InterviewCreate) -> Interview:
        interview = Interview(**data.model_dump())
        self.db.add(interview)
        await self.db.flush()
        await self.db.refresh(interview)
        return interview

    async def submit_interview_feedback(
        self, interview_id: UUID, data: InterviewFeedback
    ) -> Interview:
        result = await self.db.execute(
            select(Interview).where(
                Interview.id == interview_id, Interview.deleted_at.is_(None)
            )
        )
        interview = result.scalar_one_or_none()
        if not interview:
            raise NotFoundException("Interview")
        interview.feedback = data.feedback
        interview.rating = data.rating
        interview.status = data.status
        await self.db.flush()
        return interview

    async def kanban_board(self, job_opening_id: UUID | None = None) -> dict:
        query = select(Applicant).where(Applicant.deleted_at.is_(None))
        if job_opening_id:
            query = query.where(Applicant.job_opening_id == job_opening_id)
        result = await self.db.execute(query)
        applicants = list(result.scalars().all())
        board: dict[str, list] = {}
        for a in applicants:
            board.setdefault(a.stage, []).append(
                {"id": str(a.id), "full_name": a.full_name, "email": a.email, "rating": a.rating}
            )
        return board
