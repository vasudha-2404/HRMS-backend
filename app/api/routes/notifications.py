"""Notification routes."""

from uuid import UUID

from fastapi import APIRouter, Query, status

from app.core.dependencies import CurrentUser, DbSession, require_roles
from app.schemas.notification import NotificationCreate, NotificationResponse
from app.services.notification_service import NotificationService
from app.utils.enums import RoleName
from app.utils.pagination import build_paginated_result
from app.utils.response import success_response

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("")
async def list_notifications(
    db: DbSession,
    current_user: CurrentUser,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    unread_only: bool = False,
):
    service = NotificationService(db)
    items, total = await service.list_for_user(
        current_user.id, page, page_size, unread_only
    )
    data = build_paginated_result(
        [NotificationResponse.model_validate(n).model_dump() for n in items],
        total,
        page,
        page_size,
    )
    return success_response(data)


@router.patch("/{notification_id}/read")
async def mark_read(
    notification_id: UUID, db: DbSession, current_user: CurrentUser
):
    service = NotificationService(db)
    notification = await service.mark_read(notification_id, current_user.id)
    return success_response(
        NotificationResponse.model_validate(notification).model_dump(),
        "Marked as read",
    )


@router.post("/mark-all-read")
async def mark_all_read(db: DbSession, current_user: CurrentUser):
    service = NotificationService(db)
    count = await service.mark_all_read(current_user.id)
    return success_response({"updated": count}, "All notifications marked as read")
