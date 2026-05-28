"""Authentication service."""

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_password_hash,
    verify_password,
)
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse
from app.services.audit_service import AuditService
from app.utils.exceptions import ConflictException, UnauthorizedException


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)
        self.audit = AuditService(db)

    async def register(self, data: RegisterRequest, role_id) -> User:
        existing = await self.user_repo.get_by_email(data.email)
        if existing:
            raise ConflictException("Email already registered")

        user = User(
            email=data.email,
            hashed_password=get_password_hash(data.password),
            full_name=data.full_name,
            phone=data.phone,
            role_id=role_id,
            is_active=True,
        )
        return await self.user_repo.create(user)

    async def login(self, data: LoginRequest) -> tuple[User, TokenResponse]:
        user = await self.user_repo.get_by_email(data.email)
        if not user or not verify_password(data.password, user.hashed_password):
            raise UnauthorizedException("Invalid email or password")
        if not user.is_active:
            raise UnauthorizedException("Account is deactivated")

        user.last_login = datetime.now(timezone.utc)
        access_token = create_access_token(
            user.id,
            extra_claims={"role": user.role.name if user.role else None},
        )
        refresh_token = create_refresh_token(user.id)
        # Store a hash of the refresh token for revocation/rotation
        user.refresh_token_hash = get_password_hash(refresh_token)

        await self.audit.log("login", "auth", user=user, description="User logged in")

        tokens = TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
        )
        return user, tokens

    async def refresh_tokens(self, refresh_token: str) -> TokenResponse:
        payload = decode_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            raise UnauthorizedException("Invalid refresh token")
        sub = payload.get("sub")
        if not sub:
            raise UnauthorizedException("Invalid refresh token payload")

        user = await self.user_repo.get_with_role(UUID(sub))
        if not user or not user.is_active:
            raise UnauthorizedException("User not found")
        if not user.refresh_token_hash or not verify_password(
            refresh_token, user.refresh_token_hash
        ):
            raise UnauthorizedException("Refresh token revoked or invalid")

        new_access = create_access_token(
            user.id,
            extra_claims={"role": user.role.name if user.role else None},
        )
        new_refresh = create_refresh_token(user.id)
        user.refresh_token_hash = get_password_hash(new_refresh)

        return TokenResponse(
            access_token=new_access,
            refresh_token=new_refresh,
            token_type="bearer",
        )

    async def logout(self, user: User) -> None:
        user.refresh_token_hash = None
        await self.audit.log("logout", "auth", user=user, description="User logged out")
