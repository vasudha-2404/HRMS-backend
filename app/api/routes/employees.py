"""Employee management routes."""

from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import require_roles
from app.models.user import User
from app.schemas.employee import EmployeeCreate, EmployeeResponse, EmployeeUpdate
from app.services.employee_service import EmployeeService
from app.utils.enums import RoleName
from app.utils.pagination import build_paginated_result
from app.utils.response import success_response

router = APIRouter(prefix="/employees", tags=["Employees"])


@router.get("")
async def list_employees(
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(
        require_roles(RoleName.SUPER_ADMIN, RoleName.HR_ADMIN)
    ),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: str | None = None,
):
    service = EmployeeService(db)
    items, total = await service.list(page, page_size, search)
    data = build_paginated_result(
        [EmployeeResponse.model_validate(e).model_dump() for e in items],
        total,
        page,
        page_size,
    )
    return success_response(data)


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_employee(
    data: EmployeeCreate,
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(require_roles(RoleName.SUPER_ADMIN, RoleName.HR_ADMIN)),
):
    service = EmployeeService(db)
    employee = await service.create(data)
    return success_response(
        EmployeeResponse.model_validate(employee).model_dump(),
        "Employee created",
    )


@router.get("/{employee_id}")
async def get_employee(
    employee_id: UUID,
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(require_roles(RoleName.SUPER_ADMIN, RoleName.HR_ADMIN)),
):
    service = EmployeeService(db)
    employee = await service.get(employee_id)
    resp = EmployeeResponse.model_validate(employee).model_dump()
    if employee.user:
        resp["full_name"] = employee.user.full_name
        resp["email"] = employee.user.email
    return success_response(resp)


@router.patch("/{employee_id}")
async def update_employee(
    employee_id: UUID,
    data: EmployeeUpdate,
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(require_roles(RoleName.SUPER_ADMIN, RoleName.HR_ADMIN)),
):
    service = EmployeeService(db)
    employee = await service.update(employee_id, data)
    return success_response(
        EmployeeResponse.model_validate(employee).model_dump(),
        "Employee updated",
    )


@router.delete("/{employee_id}")
async def delete_employee(
    employee_id: UUID,
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(require_roles(RoleName.SUPER_ADMIN, RoleName.HR_ADMIN)),
):
    service = EmployeeService(db)
    await service.delete(employee_id)
    return success_response(None, "Employee deleted")
