"""API v1 router aggregation."""

from fastapi import APIRouter

from app.api.routes import (
    attendance,
    auth,
    dashboard,
    employees,
    health,
    interns,
    leaves,
    notifications,
    recruitment,
    tasks,
)

api_router = APIRouter()

api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(employees.router)
api_router.include_router(interns.router)
api_router.include_router(attendance.router)
api_router.include_router(leaves.router)
api_router.include_router(tasks.router)
api_router.include_router(recruitment.router)
api_router.include_router(notifications.router)
api_router.include_router(dashboard.router)
