"""FastAPI dependency injection."""

from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.security import decode_token
from app.models.user import User
from app.utils.enums import RoleName

security_scheme = HTTPBearer(auto_error=False)

DbSession = Annotated[AsyncSession, Depends(get_db)]
TokenCredentials = Annotated[HTTPAuthorizationCredentials | None, Depends(security_scheme)]


async def get_current_user(
    db: DbSession,
    credentials: TokenCredentials,
) -> User:
    if not credentials or not credentials.credentials:
        print("DEBUG AUTH: No credentials or token found")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    payload = decode_token(credentials.credentials)
    if not payload:
        print("DEBUG AUTH: decode_token failed to decode")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )
    
    if payload.get("type") != "access":
        print(f"DEBUG AUTH: token type is not access, got {payload.get('type')}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    user_id = payload.get("sub")
    if not user_id:
        print("DEBUG AUTH: token sub (user_id) is missing")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    result = await db.execute(
        select(User)
        .options(selectinload(User.role))
        .where(User.id == UUID(user_id), User.deleted_at.is_(None))
    )
    user = result.scalar_one_or_none()
    if not user:
        print(f"DEBUG AUTH: user with id {user_id} not found in DB")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )
        
    if not user.is_active:
        print(f"DEBUG AUTH: user {user.email} is inactive")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def require_roles(*allowed_roles: RoleName):
    """Dependency factory for RBAC."""

    async def role_checker(current_user: CurrentUser) -> User:
        if not current_user.role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No role assigned",
            )
        role_name = current_user.role.name
        allowed = {r.value for r in allowed_roles}
        if role_name not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{role_name}' not authorized for this action",
            )
        return current_user

    return role_checker
