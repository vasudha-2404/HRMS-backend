"""Authentication schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from app.schemas.common import BaseSchema


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    full_name: str = Field(min_length=2, max_length=255)
    phone: str | None = None


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class RoleResponse(BaseSchema):
    id: UUID
    name: str
    description: str | None = None


class UserResponse(BaseSchema):
    id: UUID
    email: str
    full_name: str
    phone: str | None
    is_active: bool
    is_verified: bool
    last_login: datetime | None
    role: RoleResponse | None = None


class UserUpdateRequest(BaseModel):
    full_name: str | None = None
    phone: str | None = None


class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str = Field(min_length=8)
