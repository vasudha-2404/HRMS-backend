"""Employee repository."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.employee import Employee
from app.repositories.base import BaseRepository


class EmployeeRepository(BaseRepository[Employee]):
    def __init__(self, db: AsyncSession):
        super().__init__(Employee, db)

    async def get_with_relations(self, employee_id: UUID) -> Employee | None:
        result = await self.db.execute(
            select(Employee)
            .options(
                selectinload(Employee.user),
                selectinload(Employee.department),
                selectinload(Employee.team),
            )
            .where(Employee.id == employee_id, Employee.deleted_at.is_(None))
        )
        return result.scalar_one_or_none()

    async def get_by_user_id(self, user_id: UUID) -> Employee | None:
        result = await self.db.execute(
            select(Employee).where(
                Employee.user_id == user_id, Employee.deleted_at.is_(None)
            )
        )
        return result.scalar_one_or_none()
