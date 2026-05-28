"""Recruitment ATS routes."""

from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import require_roles
from app.models.user import User
from app.schemas.recruitment import (
    ApplicantCreate,
    ApplicantResponse,
    ApplicantStageUpdate,
    InterviewCreate,
    InterviewFeedback,
    InterviewResponse,
    JobOpeningCreate,
    JobOpeningResponse,
)
from app.services.recruitment_service import RecruitmentService
from app.utils.enums import RoleName
from app.utils.pagination import build_paginated_result
from app.utils.response import success_response

router = APIRouter(prefix="/recruitment", tags=["Recruitment ATS"])


@router.get("/jobs")
async def list_jobs(
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    service = RecruitmentService(db)
    items, total = await service.list_jobs(page, page_size)
    data = build_paginated_result(
        [JobOpeningResponse.model_validate(j).model_dump() for j in items],
        total,
        page,
        page_size,
    )
    return success_response(data)


@router.post("/jobs", status_code=status.HTTP_201_CREATED)
async def create_job(
    data: JobOpeningCreate,
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(
        require_roles(RoleName.HR_ADMIN, RoleName.SUPER_ADMIN, RoleName.REVIEWER)
    ),
):
    service = RecruitmentService(db)
    job = await service.create_job(data, None)
    return success_response(
        JobOpeningResponse.model_validate(job).model_dump(),
        "Job opening created",
    )


@router.post("/applicants", status_code=status.HTTP_201_CREATED)
async def create_applicant(
    data: ApplicantCreate,
    db: AsyncSession = Depends(get_db),
):
    service = RecruitmentService(db)
    applicant = await service.create_applicant(data)
    return success_response(
        ApplicantResponse.model_validate(applicant).model_dump(),
        "Applicant created",
    )


@router.patch("/applicants/{applicant_id}/stage")
async def update_applicant_stage(
    applicant_id: UUID,
    data: ApplicantStageUpdate,
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(
        require_roles(RoleName.HR_ADMIN, RoleName.SUPER_ADMIN, RoleName.REVIEWER)
    ),
):
    service = RecruitmentService(db)
    applicant = await service.update_applicant_stage(applicant_id, data)
    return success_response(
        ApplicantResponse.model_validate(applicant).model_dump(),
        "Applicant stage updated",
    )


@router.get("/kanban")
async def get_kanban_board(
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(
        require_roles(RoleName.HR_ADMIN, RoleName.SUPER_ADMIN, RoleName.REVIEWER)
    ),
    job_opening_id: UUID | None = None,
):
    service = RecruitmentService(db)
    board = await service.kanban_board(job_opening_id)
    return success_response(board, "Kanban board retrieved")


@router.post("/interviews", status_code=status.HTTP_201_CREATED)
async def schedule_interview(
    data: InterviewCreate,
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(
        require_roles(RoleName.HR_ADMIN, RoleName.SUPER_ADMIN, RoleName.REVIEWER)
    ),
):
    service = RecruitmentService(db)
    interview = await service.schedule_interview(data)
    return success_response(
        InterviewResponse.model_validate(interview).model_dump(),
        "Interview scheduled",
    )


@router.patch("/interviews/{interview_id}/feedback")
async def submit_feedback(
    interview_id: UUID,
    data: InterviewFeedback,
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(
        require_roles(RoleName.HR_ADMIN, RoleName.SUPER_ADMIN, RoleName.REVIEWER)
    ),
):
    service = RecruitmentService(db)
    interview = await service.submit_interview_feedback(interview_id, data)
    return success_response(
        InterviewResponse.model_validate(interview).model_dump(),
        "Feedback submitted",
    )
