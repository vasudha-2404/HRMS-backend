"""Internship management routes."""

from fastapi import APIRouter, Depends, Query, status
from pydantic import BaseModel
from datetime import date

from app.core.dependencies import DbSession, require_roles
from app.models.intern import InternBatch
from app.repositories.base import BaseRepository
from app.schemas.common import TimestampSchema
from app.utils.enums import RoleName
from app.utils.pagination import build_paginated_result
from app.utils.response import success_response

router = APIRouter(prefix="/interns", tags=["Internships"])

AdminRoles = Depends(require_roles(RoleName.SUPER_ADMIN, RoleName.HR_ADMIN))


class InternBatchCreate(BaseModel):
    name: str
    start_date: date
    end_date: date
    description: str | None = None


class InternBatchResponse(TimestampSchema):
    name: str
    start_date: date
    end_date: date
    description: str | None


@router.get("/batches")
async def list_batches(
    db: DbSession,
    _: AdminRoles,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    repo = BaseRepository(InternBatch, db)
    items, total = await repo.get_all((page - 1) * page_size, page_size)
    data = build_paginated_result(
        [InternBatchResponse.model_validate(b).model_dump() for b in items],
        total,
        page,
        page_size,
    )
    return success_response(data)


@router.post("/batches", status_code=status.HTTP_201_CREATED)
async def create_batch(data: InternBatchCreate, db: DbSession, _: AdminRoles):
    batch = InternBatch(**data.model_dump())
    repo = BaseRepository(InternBatch, db)
    created = await repo.create(batch)
    return success_response(
        InternBatchResponse.model_validate(created).model_dump(),
        "Intern batch created",
    )
