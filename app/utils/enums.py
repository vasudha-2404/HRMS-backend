"""Application-wide enumerations."""

from enum import Enum


class RoleName(str, Enum):
    SUPER_ADMIN = "super_admin"
    HR_ADMIN = "hr_admin"
    TEAM_LEAD = "team_lead"
    EMPLOYEE = "employee"
    INTERN = "intern"
    REVIEWER = "reviewer"
    DEVELOPER = "developer"


class LeaveStatus(str, Enum):
    PENDING = "pending"
    TEAM_LEAD_APPROVED = "team_lead_approved"
    HR_APPROVED = "hr_approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


class LeaveType(str, Enum):
    CASUAL = "casual"
    SICK = "sick"
    EARNED = "earned"
    UNPAID = "unpaid"
    MATERNITY = "maternity"
    PATERNITY = "paternity"


class AttendanceStatus(str, Enum):
    PRESENT = "present"
    ABSENT = "absent"
    LATE = "late"
    HALF_DAY = "half_day"
    ON_LEAVE = "on_leave"
    PENDING_APPROVAL = "pending_approval"


class TaskStatus(str, Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    IN_REVIEW = "in_review"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TaskPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class ApplicantStage(str, Enum):
    APPLIED = "applied"
    SCREENING = "screening"
    INTERVIEW = "interview"
    OFFER = "offer"
    HIRED = "hired"
    REJECTED = "rejected"


class NotificationPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class NotificationType(str, Enum):
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    LEAVE = "leave"
    TASK = "task"
    ATTENDANCE = "attendance"
    RECRUITMENT = "recruitment"


class DocumentType(str, Enum):
    RESUME = "resume"
    ID_PROOF = "id_proof"
    OFFER_LETTER = "offer_letter"
    CONTRACT = "contract"
    REPORT = "report"
    OTHER = "other"


class EmploymentStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ON_LEAVE = "on_leave"
    TERMINATED = "terminated"
    PROBATION = "probation"


class EmploymentType(str, Enum):
    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    CONTRACT = "contract"
    INTERN = "intern"


class InterviewStatus(str, Enum):
    SCHEDULED = "scheduled"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"


class ProjectStatus(str, Enum):
    ACTIVE = "active"
    ON_HOLD = "on_hold"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class InternStatus(str, Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    DROPPED = "dropped"
