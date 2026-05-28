"""Authentication routes."""

from fastapi import APIRouter, Depends, status
from sqlalchemy import select

from app.core.dependencies import CurrentUser, DbSession
from app.models.role import Role
from app.schemas.auth import (
    LoginRequest,
    RefreshTokenRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)
from app.services.auth_service import AuthService
from app.utils.response import success_response

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(data: RegisterRequest, db: DbSession):
    result = await db.execute(
        select(Role).where(Role.name == "employee", Role.deleted_at.is_(None))
    )
    role = result.scalar_one_or_none()
    if not role:
        return success_response(None, "Run seed data first to create roles")

    service = AuthService(db)
    user = await service.register(data, role.id)
    return success_response(
        UserResponse.model_validate(user).model_dump(),
        "Registration successful",
    )


@router.post("/login")
async def login(data: LoginRequest, db: DbSession):
    service = AuthService(db)
    user, tokens = await service.login(data)
    return success_response(
        {
            "user": UserResponse.model_validate(user).model_dump(),
            "tokens": tokens.model_dump(),
        },
        "Login successful",
    )


@router.post("/refresh")
async def refresh_token(data: RefreshTokenRequest, db: DbSession):
    service = AuthService(db)
    tokens = await service.refresh_tokens(data.refresh_token)
    return success_response(tokens.model_dump(), "Token refreshed")


@router.post("/logout")
async def logout(current_user: CurrentUser, db: DbSession):
    service = AuthService(db)
    await service.logout(current_user)
    return success_response(None, "Logged out successfully")


@router.get("/me")
async def get_current_user_profile(current_user: CurrentUser):
    return success_response(
        UserResponse.model_validate(current_user).model_dump(),
        "Current user retrieved",
    )
