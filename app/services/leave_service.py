"""Leave management service."""

from datetime import date, datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.leave import Leave
from app.repositories.employee_repository import EmployeeRepository
from app.schemas.leave import LeaveApprovalRequest, LeaveCreate, LeaveRejectRequest
from app.utils.enums import LeaveStatus
from app.utils.exceptions import ForbiddenException, NotFoundException


class LeaveService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.employee_repo = EmployeeRepository(db)

    def _calc_days(self, start: date, end: date) -> int:
        return (end - start).days + 1

    async def apply(self, employee_id: UUID, data: LeaveCreate) -> Leave:
        leave = Leave(
            employee_id=employee_id,
            leave_type=data.leave_type,
            start_date=data.start_date,
            end_date=data.end_date,
            total_days=self._calc_days(data.start_date, data.end_date),
            reason=data.reason,
            status=LeaveStatus.PENDING.value,
        )
        self.db.add(leave)
        await self.db.flush()
        await self.db.refresh(leave)
        return leave

    async def team_lead_approve(
        self, leave_id: UUID, approver_id: UUID, data: LeaveApprovalRequest
    ) -> Leave:
        leave = await self._get_leave(leave_id)
        if leave.status != LeaveStatus.PENDING.value:
            raise ForbiddenException("Leave is not pending team lead approval")
        leave.status = LeaveStatus.TEAM_LEAD_APPROVED.value
        leave.team_lead_id = approver_id
        leave.team_lead_approved_at = datetime.now(timezone.utc)
        leave.team_lead_remarks = data.remarks
        await self.db.flush()
        return leave

    async def hr_approve(
        self, leave_id: UUID, approver_id: UUID, data: LeaveApprovalRequest
    ) -> Leave:
        leave = await self._get_leave(leave_id)
        if leave.status != LeaveStatus.TEAM_LEAD_APPROVED.value:
            raise ForbiddenException("Leave requires team lead approval first")
        leave.status = LeaveStatus.HR_APPROVED.value
        leave.hr_approved_by_id = approver_id
        leave.hr_approved_at = datetime.now(timezone.utc)
        leave.hr_remarks = data.remarks
        await self.db.flush()
        return leave

    async def reject(
        self, leave_id: UUID, data: LeaveRejectRequest, role: str
    ) -> Leave:
        leave = await self._get_leave(leave_id)
        leave.status = LeaveStatus.REJECTED.value
        leave.rejection_reason = data.rejection_reason
        await self.db.flush()
        return leave

    async def _get_leave(self, leave_id: UUID) -> Leave:
        result = await self.db.execute(
            select(Leave).where(Leave.id == leave_id, Leave.deleted_at.is_(None))
        )
        leave = result.scalar_one_or_none()
        if not leave:
            raise NotFoundException("Leave request")
        return leave

    async def list(
        self, employee_id: UUID | None, page: int, page_size: int, status: str | None = None
    ) -> tuple[list[Leave], int]:
        from sqlalchemy import func

        query = select(Leave).where(Leave.deleted_at.is_(None))
        if employee_id:
            query = query.where(Leave.employee_id == employee_id)
        if status:
            query = query.where(Leave.status == status)

        total = (
            await self.db.execute(select(func.count()).select_from(query.subquery()))
        ).scalar() or 0
        result = await self.db.execute(
            query.order_by(Leave.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        return list(result.scalars().all()), total
