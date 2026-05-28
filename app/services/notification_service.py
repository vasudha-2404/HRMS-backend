"""Notification service."""

from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification import Notification
from app.schemas.notification import NotificationCreate
from app.utils.exceptions import NotFoundException


class NotificationService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: NotificationCreate) -> Notification:
        notification = Notification(**data.model_dump())
        self.db.add(notification)
        await self.db.flush()
        await self.db.refresh(notification)
        return notification

    async def list_for_user(
        self, user_id: UUID, page: int, page_size: int, unread_only: bool = False
    ) -> tuple[list[Notification], int]:
        from sqlalchemy import func

        query = select(Notification).where(
            Notification.user_id == user_id,
            Notification.deleted_at.is_(None),
        )
        if unread_only:
            query = query.where(Notification.is_read.is_(False))

        total = (
            await self.db.execute(select(func.count()).select_from(query.subquery()))
        ).scalar() or 0
        result = await self.db.execute(
            query.order_by(Notification.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        return list(result.scalars().all()), total

    async def mark_read(self, notification_id: UUID, user_id: UUID) -> Notification:
        result = await self.db.execute(
            select(Notification).where(
                Notification.id == notification_id,
                Notification.user_id == user_id,
                Notification.deleted_at.is_(None),
            )
        )
        notification = result.scalar_one_or_none()
        if not notification:
            raise NotFoundException("Notification")
        notification.is_read = True
        await self.db.flush()
        return notification

    async def mark_all_read(self, user_id: UUID) -> int:
        result = await self.db.execute(
            update(Notification)
            .where(
                Notification.user_id == user_id,
                Notification.is_read.is_(False),
            )
            .values(is_read=True)
        )
        return result.rowcount
