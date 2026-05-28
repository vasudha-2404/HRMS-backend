"""Attendance management service."""

from datetime import date, datetime, timezone
from decimal import Decimal
from uuid import UUID

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.attendance import Attendance
from app.repositories.employee_repository import EmployeeRepository
from app.schemas.attendance import AttendanceApprovalRequest, CheckInRequest, CheckOutRequest
from app.utils.enums import AttendanceStatus
from app.utils.exceptions import ConflictException, NotFoundException


class AttendanceService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.employee_repo = EmployeeRepository(db)

    async def _get_today_record(self, employee_id: UUID) -> Attendance | None:
        today = date.today()
        result = await self.db.execute(
            select(Attendance).where(
                Attendance.employee_id == employee_id,
                Attendance.attendance_date == today,
                Attendance.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def check_in(self, employee_id: UUID, data: CheckInRequest) -> Attendance:
        existing = await self._get_today_record(employee_id)
        if existing and existing.check_in:
            raise ConflictException("Already checked in today")

        now = datetime.now(timezone.utc)
        if existing:
            existing.check_in = now
            existing.check_in_latitude = data.latitude
            existing.check_in_longitude = data.longitude
            existing.notes = data.notes
            existing.status = AttendanceStatus.PRESENT.value
            await self.db.flush()
            return existing

        record = Attendance(
            employee_id=employee_id,
            attendance_date=date.today(),
            check_in=now,
            check_in_latitude=data.latitude,
            check_in_longitude=data.longitude,
            notes=data.notes,
            status=AttendanceStatus.PENDING_APPROVAL.value,
        )
        self.db.add(record)
        await self.db.flush()
        await self.db.refresh(record)
        return record

    async def check_out(self, employee_id: UUID, data: CheckOutRequest) -> Attendance:
        record = await self._get_today_record(employee_id)
        if not record or not record.check_in:
            raise NotFoundException("Check-in record for today")
        if record.check_out:
            raise ConflictException("Already checked out today")

        now = datetime.now(timezone.utc)
        record.check_out = now
        record.check_out_latitude = data.latitude
        record.check_out_longitude = data.longitude
        if data.notes:
            record.notes = data.notes

        delta = now - record.check_in
        record.total_hours = Decimal(str(round(delta.total_seconds() / 3600, 2)))
        await self.db.flush()
        return record

    async def approve(
        self, attendance_id: UUID, approver_id: UUID, data: AttendanceApprovalRequest
    ) -> Attendance:
        result = await self.db.execute(
            select(Attendance).where(
                Attendance.id == attendance_id, Attendance.deleted_at.is_(None)
            )
        )
        record = result.scalar_one_or_none()
        if not record:
            raise NotFoundException("Attendance record")

        record.is_approved = data.is_approved
        record.approved_by_id = approver_id
        if data.is_approved:
            record.status = AttendanceStatus.PRESENT.value
        await self.db.flush()
        return record

    async def list_by_employee(
        self, employee_id: UUID, page: int, page_size: int
    ) -> tuple[list[Attendance], int]:
        from sqlalchemy import func

        base = select(Attendance).where(
            Attendance.employee_id == employee_id,
            Attendance.deleted_at.is_(None),
        )
        total = (
            await self.db.execute(select(func.count()).select_from(base.subquery()))
        ).scalar() or 0
        result = await self.db.execute(
            base.order_by(Attendance.attendance_date.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        return list(result.scalars().all()), total
