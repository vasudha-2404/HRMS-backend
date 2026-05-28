"""Leave management routes."""

from uuid import UUID

from fastapi import APIRouter, Depends, Query

from app.core.dependencies import CurrentUser, DbSession, require_roles
from app.repositories.employee_repository import EmployeeRepository
from app.schemas.leave import (
    LeaveApprovalRequest,
    LeaveCreate,
    LeaveRejectRequest,
    LeaveResponse,
)
from app.services.leave_service import LeaveService
from app.utils.enums import RoleName
from app.utils.exceptions import NotFoundException
from app.utils.pagination import build_paginated_result
from app.utils.response import success_response

router = APIRouter(prefix="/leaves", tags=["Leaves"])

TeamLeadRoles = Depends(require_roles(RoleName.TEAM_LEAD, RoleName.SUPER_ADMIN))
HRRoles = Depends(require_roles(RoleName.HR_ADMIN, RoleName.SUPER_ADMIN))


async def _get_employee_id(db, user) -> UUID:
    repo = EmployeeRepository(db)
    employee = await repo.get_by_user_id(user.id)
    if not employee:
        raise NotFoundException("Employee profile")
    return employee.id


@router.post("/apply")
async def apply_leave(data: LeaveCreate, db: DbSession, current_user: CurrentUser):
    employee_id = await _get_employee_id(db, current_user)
    service = LeaveService(db)
    leave = await service.apply(employee_id, data)
    return success_response(
        LeaveResponse.model_validate(leave).model_dump(),
        "Leave application submitted",
    )


@router.get("")
async def list_leaves(
    db: DbSession,
    current_user: CurrentUser,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: str | None = None,
):
    employee_id = await _get_employee_id(db, current_user)
    service = LeaveService(db)
    items, total = await service.list(employee_id, page, page_size, status)
    data = build_paginated_result(
        [LeaveResponse.model_validate(l).model_dump() for l in items],
        total,
        page,
        page_size,
    )
    return success_response(data)


@router.get("/all")
async def list_all_leaves(
    db: DbSession,
    _: HRRoles,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: str | None = None,
):
    service = LeaveService(db)
    items, total = await service.list(None, page, page_size, status)
    data = build_paginated_result(
        [LeaveResponse.model_validate(l).model_dump() for l in items],
        total,
        page,
        page_size,
    )
    return success_response(data)


@router.patch("/{leave_id}/team-lead-approve")
async def team_lead_approve(
    leave_id: UUID,
    data: LeaveApprovalRequest,
    db: DbSession,
    current_user: CurrentUser,
    _: TeamLeadRoles,
):
    approver_id = await _get_employee_id(db, current_user)
    service = LeaveService(db)
    leave = await service.team_lead_approve(leave_id, approver_id, data)
    return success_response(
        LeaveResponse.model_validate(leave).model_dump(),
        "Team lead approved",
    )


@router.patch("/{leave_id}/hr-approve")
async def hr_approve(
    leave_id: UUID,
    data: LeaveApprovalRequest,
    db: DbSession,
    current_user: CurrentUser,
    _: HRRoles,
):
    approver_id = await _get_employee_id(db, current_user)
    service = LeaveService(db)
    leave = await service.hr_approve(leave_id, approver_id, data)
    return success_response(
        LeaveResponse.model_validate(leave).model_dump(),
        "HR approved",
    )


@router.patch("/{leave_id}/reject")
async def reject_leave(
    leave_id: UUID,
    data: LeaveRejectRequest,
    db: DbSession,
    current_user: CurrentUser,
    _: TeamLeadRoles,
):
    role = current_user.role.name if current_user.role else ""
    service = LeaveService(db)
    leave = await service.reject(leave_id, data, role)
    return success_response(
        LeaveResponse.model_validate(leave).model_dump(),
        "Leave rejected",
    )
