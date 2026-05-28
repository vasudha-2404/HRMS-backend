"""Generic async repository base."""

from datetime import datetime, timezone
from typing import Any, Generic, TypeVar
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.base import BaseModel

ModelT = TypeVar("ModelT", bound=BaseModel)


class BaseRepository(Generic[ModelT]):
    def __init__(self, model: type[ModelT], db: AsyncSession):
        self.model = model
        self.db = db

    async def get_by_id(self, id: UUID, include_deleted: bool = False) -> ModelT | None:
        query = select(self.model).where(self.model.id == id)
        if not include_deleted:
            query = query.where(self.model.deleted_at.is_(None))
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_all(
        self,
        offset: int = 0,
        limit: int = 20,
        search: str | None = None,
        search_fields: list[str] | None = None,
        order_by: str | None = None,
        order_desc: bool = True,
    ) -> tuple[list[ModelT], int]:
        query = select(self.model).where(self.model.deleted_at.is_(None))

        if search and search_fields:
            from sqlalchemy import or_

            conditions = []
            for field in search_fields:
                col = getattr(self.model, field, None)
                if col is not None:
                    conditions.append(col.ilike(f"%{search}%"))
            if conditions:
                query = query.where(or_(*conditions))

        count_query = select(func.count()).select_from(query.subquery())
        total = (await self.db.execute(count_query)).scalar() or 0

        if order_by and hasattr(self.model, order_by):
            col = getattr(self.model, order_by)
            query = query.order_by(col.desc() if order_desc else col.asc())
        else:
            query = query.order_by(self.model.created_at.desc())

        query = query.offset(offset).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all()), total

    async def create(self, obj: ModelT) -> ModelT:
        self.db.add(obj)
        await self.db.flush()
        await self.db.refresh(obj)
        return obj

    async def update(self, obj: ModelT, data: dict[str, Any]) -> ModelT:
        for key, value in data.items():
            if value is not None and hasattr(obj, key):
                setattr(obj, key, value)
        await self.db.flush()
        await self.db.refresh(obj)
        return obj

    async def soft_delete(self, obj: ModelT) -> None:
        obj.deleted_at = datetime.now(timezone.utc)
        await self.db.flush()
