"""Task management routes."""

from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from app.core.dependencies import CurrentUser, DbSession, require_roles
from app.repositories.employee_repository import EmployeeRepository
from app.schemas.task import TaskCommentCreate, TaskCommentResponse, TaskCreate, TaskResponse, TaskUpdate
from app.services.task_service import TaskService
from app.utils.enums import RoleName
from app.utils.pagination import build_paginated_result
from app.utils.response import success_response

router = APIRouter(prefix="/tasks", tags=["Tasks"])

ManagerRoles = Depends(require_roles(RoleName.SUPER_ADMIN, RoleName.HR_ADMIN, RoleName.TEAM_LEAD))


@router.get("")
async def list_tasks(
    db: DbSession,
    current_user: CurrentUser,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: str | None = None,
):
    repo = EmployeeRepository(db)
    employee = await repo.get_by_user_id(current_user.id)
    assignee_id = employee.id if employee else None
    service = TaskService(db)
    items, total = await service.list(page, page_size, assignee_id, status)
    data = build_paginated_result(
        [TaskResponse.model_validate(t).model_dump() for t in items],
        total,
        page,
        page_size,
    )
    return success_response(data)


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_task(data: TaskCreate, db: DbSession, current_user: CurrentUser, _: ManagerRoles):
    repo = EmployeeRepository(db)
    employee = await repo.get_by_user_id(current_user.id)
    service = TaskService(db)
    task = await service.create(data, employee.id if employee else None)
    return success_response(TaskResponse.model_validate(task).model_dump(), "Task created")


@router.get("/{task_id}")
async def get_task(task_id: UUID, db: DbSession, current_user: CurrentUser):
    service = TaskService(db)
    task = await service.get(task_id)
    return success_response(TaskResponse.model_validate(task).model_dump())


@router.patch("/{task_id}")
async def update_task(
    task_id: UUID, data: TaskUpdate, db: DbSession, current_user: CurrentUser
):
    service = TaskService(db)
    task = await service.update(task_id, data)
    return success_response(TaskResponse.model_validate(task).model_dump(), "Task updated")


@router.delete("/{task_id}")
async def delete_task(task_id: UUID, db: DbSession, _: ManagerRoles):
    service = TaskService(db)
    await service.delete(task_id)
    return success_response(None, "Task deleted")


@router.post("/{task_id}/comments", status_code=status.HTTP_201_CREATED)
async def add_comment(
    task_id: UUID,
    data: TaskCommentCreate,
    db: DbSession,
    current_user: CurrentUser,
):
    service = TaskService(db)
    comment = await service.add_comment(task_id, current_user.id, data)
    return success_response(
        TaskCommentResponse.model_validate(comment).model_dump(),
        "Comment added",
    )
