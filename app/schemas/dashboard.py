"""Dashboard analytics schemas."""

from pydantic import BaseModel


class AttendanceStats(BaseModel):
    total_records: int
    present_count: int
    absent_count: int
    late_count: int
    pending_approval: int
    average_hours: float | None


class LeaveStats(BaseModel):
    total_requests: int
    pending: int
    approved: int
    rejected: int
    by_type: dict[str, int]


class TaskStats(BaseModel):
    total: int
    todo: int
    in_progress: int
    completed: int
    overdue: int
    completion_rate: float


class ATSStats(BaseModel):
    active_jobs: int
    total_applicants: int
    by_stage: dict[str, int]
    interviews_scheduled: int


class EmployeeStats(BaseModel):
    total_employees: int
    active: int
    on_leave: int
    by_department: dict[str, int]
