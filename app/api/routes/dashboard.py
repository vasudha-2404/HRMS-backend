"""Dashboard analytics routes."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import require_roles
from app.models.user import User
from app.services.dashboard_service import DashboardService
from app.utils.enums import RoleName
from app.utils.response import success_response

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/attendance")
async def attendance_dashboard(
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(
        require_roles(RoleName.SUPER_ADMIN, RoleName.HR_ADMIN, RoleName.TEAM_LEAD)
    ),
):
    service = DashboardService(db)
    stats = await service.attendance_stats()
    return success_response(stats.model_dump())


@router.get("/leaves")
async def leave_dashboard(
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(
        require_roles(RoleName.SUPER_ADMIN, RoleName.HR_ADMIN, RoleName.TEAM_LEAD)
    ),
):
    service = DashboardService(db)
    stats = await service.leave_stats()
    return success_response(stats.model_dump())


@router.get("/tasks")
async def task_dashboard(
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(
        require_roles(RoleName.SUPER_ADMIN, RoleName.HR_ADMIN, RoleName.TEAM_LEAD)
    ),
):
    service = DashboardService(db)
    stats = await service.task_stats()
    return success_response(stats.model_dump())


@router.get("/ats")
async def ats_dashboard(
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(
        require_roles(RoleName.SUPER_ADMIN, RoleName.HR_ADMIN, RoleName.TEAM_LEAD)
    ),
):
    service = DashboardService(db)
    stats = await service.ats_stats()
    return success_response(stats.model_dump())


@router.get("/employees")
async def employee_dashboard(
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(
        require_roles(RoleName.SUPER_ADMIN, RoleName.HR_ADMIN, RoleName.TEAM_LEAD)
    ),
):
    service = DashboardService(db)
    stats = await service.employee_stats()
    return success_response(stats.model_dump())
