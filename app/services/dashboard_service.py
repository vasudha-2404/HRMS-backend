"""Dashboard analytics service."""

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.attendance import Attendance
from app.models.employee import Employee
from app.models.leave import Leave
from app.models.recruitment import Applicant, Interview, JobOpening
from app.models.task import Task
from app.schemas.dashboard import ATSStats, AttendanceStats, EmployeeStats, LeaveStats, TaskStats
from app.utils.enums import AttendanceStatus, LeaveStatus, TaskStatus


class DashboardService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def attendance_stats(self) -> AttendanceStats:
        base = select(Attendance).where(Attendance.deleted_at.is_(None))
        total = (
            await self.db.execute(select(func.count()).select_from(base.subquery()))
        ).scalar() or 0

        async def count_status(status: str) -> int:
            q = base.where(Attendance.status == status)
            return (
                await self.db.execute(select(func.count()).select_from(q.subquery()))
            ).scalar() or 0

        avg_hours = (
            await self.db.execute(
                select(func.avg(Attendance.total_hours)).where(
                    Attendance.deleted_at.is_(None),
                    Attendance.total_hours.isnot(None),
                )
            )
        ).scalar()

        pending = (
            await self.db.execute(
                select(func.count()).where(
                    Attendance.deleted_at.is_(None),
                    Attendance.is_approved.is_(False),
                )
            )
        ).scalar() or 0

        return AttendanceStats(
            total_records=total,
            present_count=await count_status(AttendanceStatus.PRESENT.value),
            absent_count=await count_status(AttendanceStatus.ABSENT.value),
            late_count=await count_status(AttendanceStatus.LATE.value),
            pending_approval=pending,
            average_hours=float(avg_hours) if avg_hours else None,
        )

    async def leave_stats(self) -> LeaveStats:
        base = select(Leave).where(Leave.deleted_at.is_(None))
        total = (
            await self.db.execute(select(func.count()).select_from(base.subquery()))
        ).scalar() or 0

        async def count_status(status: str) -> int:
            q = base.where(Leave.status == status)
            return (
                await self.db.execute(select(func.count()).select_from(q.subquery()))
            ).scalar() or 0

        type_result = await self.db.execute(
            select(Leave.leave_type, func.count())
            .where(Leave.deleted_at.is_(None))
            .group_by(Leave.leave_type)
        )
        by_type = {row[0]: row[1] for row in type_result.all()}

        return LeaveStats(
            total_requests=total,
            pending=await count_status(LeaveStatus.PENDING.value),
            approved=await count_status(LeaveStatus.HR_APPROVED.value),
            rejected=await count_status(LeaveStatus.REJECTED.value),
            by_type=by_type,
        )

    async def task_stats(self) -> TaskStats:
        base = select(Task).where(Task.deleted_at.is_(None))
        total = (
            await self.db.execute(select(func.count()).select_from(base.subquery()))
        ).scalar() or 0

        async def count_status(status: str) -> int:
            q = base.where(Task.status == status)
            return (
                await self.db.execute(select(func.count()).select_from(q.subquery()))
            ).scalar() or 0

        completed = await count_status(TaskStatus.COMPLETED.value)
        return TaskStats(
            total=total,
            todo=await count_status(TaskStatus.TODO.value),
            in_progress=await count_status(TaskStatus.IN_PROGRESS.value),
            completed=completed,
            overdue=0,
            completion_rate=round(completed / total * 100, 2) if total else 0.0,
        )

    async def ats_stats(self) -> ATSStats:
        active_jobs = (
            await self.db.execute(
                select(func.count()).where(
                    JobOpening.deleted_at.is_(None),
                    JobOpening.is_active.is_(True),
                )
            )
        ).scalar() or 0

        total_applicants = (
            await self.db.execute(
                select(func.count()).where(Applicant.deleted_at.is_(None))
            )
        ).scalar() or 0

        stage_result = await self.db.execute(
            select(Applicant.stage, func.count())
            .where(Applicant.deleted_at.is_(None))
            .group_by(Applicant.stage)
        )
        by_stage = {row[0]: row[1] for row in stage_result.all()}

        interviews = (
            await self.db.execute(
                select(func.count()).where(
                    Interview.deleted_at.is_(None),
                    Interview.status == "scheduled",
                )
            )
        ).scalar() or 0

        return ATSStats(
            active_jobs=active_jobs,
            total_applicants=total_applicants,
            by_stage=by_stage,
            interviews_scheduled=interviews,
        )

    async def employee_stats(self) -> EmployeeStats:
        total = (
            await self.db.execute(
                select(func.count()).where(Employee.deleted_at.is_(None))
            )
        ).scalar() or 0

        active = (
            await self.db.execute(
                select(func.count()).where(
                    Employee.deleted_at.is_(None),
                    Employee.employment_status == "active",
                )
            )
        ).scalar() or 0

        on_leave = (
            await self.db.execute(
                select(func.count()).where(
                    Employee.deleted_at.is_(None),
                    Employee.employment_status == "on_leave",
                )
            )
        ).scalar() or 0

        return EmployeeStats(
            total_employees=total,
            active=active,
            on_leave=on_leave,
            by_department={},
        )
