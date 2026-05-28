"""Dashboard analytics routes."""

from fastapi import APIRouter, Depends

from app.core.dependencies import DbSession, require_roles
from app.services.dashboard_service import DashboardService
from app.utils.enums import RoleName
from app.utils.response import success_response

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

AdminRoles = Depends(require_roles(RoleName.SUPER_ADMIN, RoleName.HR_ADMIN, RoleName.TEAM_LEAD))


@router.get("/attendance")
async def attendance_dashboard(db: DbSession, _: AdminRoles):
    service = DashboardService(db)
    stats = await service.attendance_stats()
    return success_response(stats.model_dump())


@router.get("/leaves")
async def leave_dashboard(db: DbSession, _: AdminRoles):
    service = DashboardService(db)
    stats = await service.leave_stats()
    return success_response(stats.model_dump())


@router.get("/tasks")
async def task_dashboard(db: DbSession, _: AdminRoles):
    service = DashboardService(db)
    stats = await service.task_stats()
    return success_response(stats.model_dump())


@router.get("/ats")
async def ats_dashboard(db: DbSession, _: AdminRoles):
    service = DashboardService(db)
    stats = await service.ats_stats()
    return success_response(stats.model_dump())


@router.get("/employees")
async def employee_dashboard(db: DbSession, _: AdminRoles):
    service = DashboardService(db)
    stats = await service.employee_stats()
    return success_response(stats.model_dump())
