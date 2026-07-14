"""Authentication routes."""

from datetime import datetime, timezone
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy import select
import sqlalchemy as sa
from sqlalchemy.orm import selectinload
from app.models.user import User

from app.core.dependencies import CurrentUser, DbSession
from app.models.role import Role
from app.schemas.auth import (
    LoginRequest,
    RefreshTokenRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
    CompleteProfileRequest,
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
    user = await service.user_repo.get_by_email(data.email)
    if not user:
        raise UnauthorizedException("Invalid email or password")
        
    # Check if role matches
    requested_role = data.role
    if requested_role == "HR":
        requested_role = "hr_admin"
    elif requested_role == "Manager":
        requested_role = "team_lead"
    elif requested_role == "Admin":
        requested_role = "super_admin"
    else:
        requested_role = requested_role.lower()

    if user.role.name != requested_role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"You are not registered as {data.role}."
        )

    user, tokens = await service.login(data)
    return success_response(
        {
            "profile_incomplete": not user.onboarding_completed,
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


from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from app.core.config import settings
from app.utils.exceptions import UnauthorizedException
from app.schemas.auth import GoogleTokenRequest

import httpx

@router.post("/google")
async def google_login(data: GoogleTokenRequest, db: DbSession):
    email = None
    full_name = "Google User"
    
    # Try ID Token verification first
    try:
        import requests
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        session = requests.Session()
        session.verify = False
        request_handler = google_requests.Request(session=session)
        
        id_info = id_token.verify_oauth2_token(
            data.id_token,
            request_handler,
            settings.GOOGLE_WEB_CLIENT_ID
        )
        if id_info["iss"] in ["accounts.google.com", "https://accounts.google.com"]:
            email = id_info.get("email")
            full_name = id_info.get("name", "Google User")
    except Exception as e:
        print(f"ID Token verification exception: {e}")
        pass

    # If ID Token verification failed, try Access Token verification
    if not email:
        try:
            async with httpx.AsyncClient(verify=False) as client:
                res = await client.get(
                    "https://oauth2.googleapis.com/tokeninfo",
                    params={"access_token": data.id_token}
                )
                if res.status_code == 200:
                    token_info = res.json()
                    # Verify target client ID to prevent token substitution attacks
                    aud = token_info.get("aud")
                    if aud == settings.GOOGLE_WEB_CLIENT_ID:
                        email = token_info.get("email")
                        full_name = token_info.get("name", "Google User")
        except Exception as e:
            print(f"Access Token verification exception: {e}")
            pass

    if not email:
        raise UnauthorizedException("Invalid Google token ID or Access Token")
            
    # Find user or create if not exists
    service = AuthService(db)
    user = await db.scalar(
        select(User).options(selectinload(User.role)).where(User.email == email, User.deleted_at.is_(None))
    )
    
    # Check if role matches if user exists
    requested_role = data.role
    if requested_role == "HR":
        requested_role = "hr_admin"
    elif requested_role == "Manager":
        requested_role = "team_lead"
    elif requested_role == "Admin":
        requested_role = "super_admin"
    else:
        requested_role = requested_role.lower()

    if user and user.role.name != requested_role:
        raise HTTPException(
            status_code=403,
            detail=f"You are not registered as {data.role}."
        )

    if not user:
        # Fetch target role matching selection
        result = await db.execute(
            select(Role).where(sa.func.lower(Role.name) == sa.func.lower(requested_role), Role.deleted_at.is_(None))
        )
        role = result.scalar_one_or_none()
        if not role:
            # Fallback to employee if custom/unseeded role
            result = await db.execute(
                select(Role).where(Role.name == "employee", Role.deleted_at.is_(None))
            )
            role = result.scalar_one_or_none()
            if not role:
                raise HTTPException(status_code=500, detail="Default role employee not found. Run seed data first.")
            
        # Create user with onboarding_completed = False
        import secrets
        from app.core.security import get_password_hash
        user = User(
            email=email,
            hashed_password=get_password_hash(secrets.token_hex(16)),
            full_name=full_name,
            role_id=role.id,
            is_active=True,
            is_verified=True,
            onboarding_completed=False,
        )
        user = await service.user_repo.create(user)
        user = await db.scalar(
            select(User).options(selectinload(User.role)).where(User.id == user.id)
        )

    if not user.onboarding_completed:
        # Generate JWT Auth tokens so that client can authenticate /complete-profile
        user.last_login = datetime.now(timezone.utc)
        from app.core.security import create_access_token, create_refresh_token, get_password_hash
        from app.schemas.auth import TokenResponse
        
        access_token = create_access_token(
            user.id,
            extra_claims={"role": user.role.name if user.role else None},
        )
        refresh_token = create_refresh_token(user.id)
        user.refresh_token_hash = get_password_hash(refresh_token)
        await db.commit()

        tokens = TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
        )
        return success_response(
            {
                "profile_incomplete": True,
                "user": UserResponse.model_validate(user).model_dump(),
                "tokens": tokens.model_dump(),
            },
            "Profile incomplete. Onboarding required.",
        )

    # Generate JWT Auth tokens for completed profile
    user.last_login = datetime.now(timezone.utc)
    from app.core.security import create_access_token, create_refresh_token, get_password_hash
    from app.schemas.auth import TokenResponse
    
    access_token = create_access_token(
        user.id,
        extra_claims={"role": user.role.name if user.role else None},
    )
    refresh_token = create_refresh_token(user.id)
    user.refresh_token_hash = get_password_hash(refresh_token)
    
    await service.audit.log("login", "auth", user=user, description="User logged in via Google")
    
    tokens = TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
    )
    
    return success_response(
        {
            "profile_incomplete": False,
            "user": UserResponse.model_validate(user).model_dump(),
            "tokens": tokens.model_dump(),
        },
        "Google login successful",
    )


from app.models.employee import Employee
from app.models.department import Department
from app.utils.enums import EmploymentStatus
from datetime import date

@router.post("/complete-profile")
async def complete_profile(data: CompleteProfileRequest, current_user: CurrentUser, db: DbSession):
    # Find user in DB
    user = await db.scalar(
        select(User).options(selectinload(User.role)).where(User.id == current_user.id)
    )
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    # Map role selection name to DB role name
    requested_role = data.role
    if requested_role == "HR":
        requested_role = "hr_admin"
    elif requested_role == "Manager":
        requested_role = "team_lead"
    elif requested_role == "Admin":
        requested_role = "super_admin"
    else:
        requested_role = requested_role.lower()

    # Find the corresponding Role in DB
    result = await db.execute(
        select(Role).where(sa.func.lower(Role.name) == sa.func.lower(requested_role), Role.deleted_at.is_(None))
    )
    role = result.scalar_one_or_none()
    if not role:
        # Fallback to employee
        result = await db.execute(
            select(Role).where(Role.name == "employee", Role.deleted_at.is_(None))
        )
        role = result.scalar_one_or_none()
        if not role:
            raise HTTPException(status_code=500, detail="Default role employee not found. Run seed data first.")

    # Update user properties
    user.role_id = role.id
    user.full_name = data.full_name
    if data.phone:
        user.phone = data.phone
    user.onboarding_completed = True

    # Find or create department
    dept = None
    if data.department:
        dept_result = await db.execute(
            select(Department).where(sa.func.lower(Department.name) == sa.func.lower(data.department))
        )
        dept = dept_result.scalar_one_or_none()
        if not dept:
            # Create a new department with a unique code
            base_code = data.department[:3].upper()
            code = base_code
            suffix = 1
            while True:
                existing_dept = await db.scalar(
                    select(Department).where(Department.code == code)
                )
                if not existing_dept:
                    break
                code = f"{base_code[:2]}{suffix}"
                suffix += 1

            dept = Department(
                name=data.department,
                code=code,
                description=f"{data.department} Department",
            )
            db.add(dept)
            await db.flush()

    # Generate employee code if not provided
    emp_code = data.employee_code
    if not emp_code:
        import random
        emp_code = f"EMP-{random.randint(1000, 9999)}"

    # Create the corresponding Employee record if not exists
    emp_result = await db.execute(
        select(Employee).where(Employee.user_id == user.id)
    )
    employee = emp_result.scalar_one_or_none()
    if not employee:
        employee = Employee(
            user_id=user.id,
            employee_code=emp_code,
            designation=data.role,
            date_of_joining=date.today(),
            employment_status=EmploymentStatus.ACTIVE,
            department_id=dept.id if dept else None,
        )
        db.add(employee)

    await db.commit()
    
    # Reload user
    user = await db.scalar(
        select(User).options(selectinload(User.role)).where(User.id == user.id)
    )

    # Generate tokens
    from app.core.security import create_access_token, create_refresh_token, get_password_hash
    from app.schemas.auth import TokenResponse
    
    access_token = create_access_token(
        user.id,
        extra_claims={"role": user.role.name if user.role else None},
    )
    refresh_token = create_refresh_token(user.id)
    user.refresh_token_hash = get_password_hash(refresh_token)
    await db.commit()

    tokens = TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
    )

    return success_response(
        {
            "profile_incomplete": False,
            "user": UserResponse.model_validate(user).model_dump(),
            "tokens": tokens.model_dump(),
        },
        "Profile onboarding completed successfully",
    )


@router.post("/reset-test-user")
async def reset_test_user(email: str, db: DbSession):
    user = await db.scalar(
        select(User).where(User.email == email)
    )
    if user:
        user.onboarding_completed = False
        from app.models.employee import Employee
        emp_result = await db.execute(
            select(Employee).where(Employee.user_id == user.id)
        )
        employee = emp_result.scalar_one_or_none()
        if employee:
            await db.delete(employee)
        await db.commit()
        return success_response(None, f"Reset onboarding status for {email}")
    return success_response(None, "User not found")


