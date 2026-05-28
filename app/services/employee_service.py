"""Employee management service."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.employee import Employee
from app.repositories.employee_repository import EmployeeRepository
from app.schemas.employee import EmployeeCreate, EmployeeUpdate
from app.utils.exceptions import ConflictException, NotFoundException


class EmployeeService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = EmployeeRepository(db)

    async def create(self, data: EmployeeCreate) -> Employee:
        existing = await self.repo.get_by_user_id(data.user_id)
        if existing:
            raise ConflictException("Employee profile already exists for this user")
        employee = Employee(**data.model_dump())
        return await self.repo.create(employee)

    async def get(self, employee_id: UUID) -> Employee:
        employee = await self.repo.get_with_relations(employee_id)
        if not employee:
            raise NotFoundException("Employee")
        return employee

    async def list(
        self, page: int, page_size: int, search: str | None = None
    ) -> tuple[list[Employee], int]:
        return await self.repo.get_all(
            offset=(page - 1) * page_size,
            limit=page_size,
            search=search,
            search_fields=["employee_code", "designation"],
        )

    async def update(self, employee_id: UUID, data: EmployeeUpdate) -> Employee:
        employee = await self.get(employee_id)
        return await self.repo.update(employee, data.model_dump(exclude_unset=True))

    async def delete(self, employee_id: UUID) -> None:
        employee = await self.get(employee_id)
        await self.repo.soft_delete(employee)
