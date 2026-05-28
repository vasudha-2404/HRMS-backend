"""SQLAlchemy models package - import all models for Alembic."""

from app.models.activity_log import ActivityLog
from app.models.attendance import Attendance
from app.models.department import Department, Team
from app.models.document import Document
from app.models.employee import Employee
from app.models.intern import Intern, InternBatch
from app.models.leave import Leave
from app.models.notification import Notification
from app.models.project import Project
from app.models.recruitment import Applicant, Interview, JobOpening
from app.models.role import Permission, Role, RolePermission
from app.models.task import Report, Task, TaskComment
from app.models.user import User

__all__ = [
    "User",
    "Role",
    "Permission",
    "RolePermission",
    "Employee",
    "Department",
    "Team",
    "Intern",
    "InternBatch",
    "Attendance",
    "Leave",
    "Task",
    "TaskComment",
    "Report",
    "Applicant",
    "Interview",
    "JobOpening",
    "Notification",
    "ActivityLog",
    "Document",
    "Project",
]
