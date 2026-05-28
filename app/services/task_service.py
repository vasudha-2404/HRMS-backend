"""Task management service."""

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.task import Task, TaskComment
from app.schemas.task import TaskCommentCreate, TaskCreate, TaskUpdate
from app.utils.enums import TaskStatus
from app.utils.exceptions import NotFoundException


class TaskService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: TaskCreate, assigned_by_id: UUID | None) -> Task:
        task = Task(**data.model_dump(), assigned_by_id=assigned_by_id)
        self.db.add(task)
        await self.db.flush()
        await self.db.refresh(task)
        return task

    async def get(self, task_id: UUID) -> Task:
        result = await self.db.execute(
            select(Task).where(Task.id == task_id, Task.deleted_at.is_(None))
        )
        task = result.scalar_one_or_none()
        if not task:
            raise NotFoundException("Task")
        return task

    async def update(self, task_id: UUID, data: TaskUpdate) -> Task:
        task = await self.get(task_id)
        update_data = data.model_dump(exclude_unset=True)
        if update_data.get("status") == TaskStatus.COMPLETED.value:
            task.completed_at = datetime.now(timezone.utc)
        for k, v in update_data.items():
            setattr(task, k, v)
        await self.db.flush()
        return task

    async def add_comment(
        self, task_id: UUID, user_id: UUID, data: TaskCommentCreate
    ) -> TaskComment:
        await self.get(task_id)
        comment = TaskComment(task_id=task_id, user_id=user_id, content=data.content)
        self.db.add(comment)
        await self.db.flush()
        await self.db.refresh(comment)
        return comment

    async def list(
        self,
        page: int,
        page_size: int,
        assignee_id: UUID | None = None,
        status: str | None = None,
    ) -> tuple[list[Task], int]:
        from sqlalchemy import func

        query = select(Task).where(Task.deleted_at.is_(None))
        if assignee_id:
            query = query.where(Task.assignee_id == assignee_id)
        if status:
            query = query.where(Task.status == status)

        total = (
            await self.db.execute(select(func.count()).select_from(query.subquery()))
        ).scalar() or 0
        result = await self.db.execute(
            query.order_by(Task.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        return list(result.scalars().all()), total

    async def delete(self, task_id: UUID) -> None:
        task = await self.get(task_id)
        task.soft_delete()
        await self.db.flush()
