"""Employee schemas."""

from datetime import date
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.common import BaseSchema, TimestampSchema


class EmployeeCreate(BaseModel):
    user_id: UUID
    employee_code: str = Field(max_length=20)
    designation: str
    date_of_joining: date
    department_id: UUID | None = None
    team_id: UUID | None = None
    manager_id: UUID | None = None
    date_of_birth: date | None = None
    gender: str | None = None
    address: str | None = None
    emergency_contact: str | None = None
    salary: Decimal | None = None


class EmployeeUpdate(BaseModel):
    designation: str | None = None
    department_id: UUID | None = None
    team_id: UUID | None = None
    manager_id: UUID | None = None
    employment_status: str | None = None
    salary: Decimal | None = None
    address: str | None = None
    emergency_contact: str | None = None


class EmployeeResponse(TimestampSchema):
    employee_code: str
    designation: str
    date_of_joining: date
    employment_status: str
    user_id: UUID
    department_id: UUID | None
    team_id: UUID | None
    manager_id: UUID | None
    full_name: str | None = None
    email: str | None = None
