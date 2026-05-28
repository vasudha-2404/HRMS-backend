"""Attendance routes."""

from uuid import UUID

from fastapi import APIRouter, Depends, Query

from app.core.dependencies import CurrentUser, DbSession, require_roles
from app.repositories.employee_repository import EmployeeRepository
from app.schemas.attendance import (
    AttendanceApprovalRequest,
    AttendanceResponse,
    CheckInRequest,
    CheckOutRequest,
)
from app.services.attendance_service import AttendanceService
from app.utils.enums import RoleName
from app.utils.exceptions import NotFoundException
from app.utils.pagination import build_paginated_result
from app.utils.response import success_response

router = APIRouter(prefix="/attendance", tags=["Attendance"])

LeadRoles = Depends(require_roles(RoleName.SUPER_ADMIN, RoleName.HR_ADMIN, RoleName.TEAM_LEAD))


async def _get_employee_id(db, user) -> UUID:
    repo = EmployeeRepository(db)
    employee = await repo.get_by_user_id(user.id)
    if not employee:
        raise NotFoundException("Employee profile")
    return employee.id


@router.post("/check-in")
async def check_in(data: CheckInRequest, db: DbSession, current_user: CurrentUser):
    employee_id = await _get_employee_id(db, current_user)
    service = AttendanceService(db)
    record = await service.check_in(employee_id, data)
    return success_response(
        AttendanceResponse.model_validate(record).model_dump(),
        "Checked in successfully",
    )


@router.post("/check-out")
async def check_out(data: CheckOutRequest, db: DbSession, current_user: CurrentUser):
    employee_id = await _get_employee_id(db, current_user)
    service = AttendanceService(db)
    record = await service.check_out(employee_id, data)
    return success_response(
        AttendanceResponse.model_validate(record).model_dump(),
        "Checked out successfully",
    )


@router.get("/my")
async def my_attendance(
    db: DbSession,
    current_user: CurrentUser,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    employee_id = await _get_employee_id(db, current_user)
    service = AttendanceService(db)
    items, total = await service.list_by_employee(employee_id, page, page_size)
    data = build_paginated_result(
        [AttendanceResponse.model_validate(a).model_dump() for a in items],
        total,
        page,
        page_size,
    )
    return success_response(data)


@router.patch("/{attendance_id}/approve")
async def approve_attendance(
    attendance_id: UUID,
    data: AttendanceApprovalRequest,
    db: DbSession,
    current_user: CurrentUser,
    _: LeadRoles,
):
    employee_id = await _get_employee_id(db, current_user)
    service = AttendanceService(db)
    record = await service.approve(attendance_id, employee_id, data)
    return success_response(
        AttendanceResponse.model_validate(record).model_dump(),
        "Attendance approved",
    )
