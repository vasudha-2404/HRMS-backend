"""Seed database with roles, permissions, and sample users."""

import asyncio
from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings
from app.core.security import get_password_hash
from app.models.department import Department
from app.models.employee import Employee
from app.models.role import Permission, Role, RolePermission
from app.models.user import User
from app.utils.enums import RoleName

ROLES = [
    (RoleName.SUPER_ADMIN, "Full system access"),
    (RoleName.HR_ADMIN, "HR administration"),
    (RoleName.TEAM_LEAD, "Team management"),
    (RoleName.EMPLOYEE, "Standard employee"),
    (RoleName.INTERN, "Intern access"),
    (RoleName.REVIEWER, "Interview reviewer"),
]

PERMISSIONS = [
    ("users.read", "Read Users", "users"),
    ("users.write", "Write Users", "users"),
    ("employees.read", "Read Employees", "employees"),
    ("employees.write", "Write Employees", "employees"),
    ("attendance.read", "Read Attendance", "attendance"),
    ("attendance.write", "Write Attendance", "attendance"),
    ("leaves.read", "Read Leaves", "leaves"),
    ("leaves.write", "Write Leaves", "leaves"),
    ("leaves.approve", "Approve Leaves", "leaves"),
    ("tasks.read", "Read Tasks", "tasks"),
    ("tasks.write", "Write Tasks", "tasks"),
    ("recruitment.read", "Read Recruitment", "recruitment"),
    ("recruitment.write", "Write Recruitment", "recruitment"),
    ("dashboard.read", "Read Dashboard", "dashboard"),
]


async def seed() -> None:
    engine = create_async_engine(settings.DATABASE_URL, echo=settings.DEBUG)
    Session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with Session() as db:
        role_map: dict[str, Role] = {}
        for name, desc in ROLES:
            result = await db.execute(select(Role).where(Role.name == name.value))
            role = result.scalar_one_or_none()
            if not role:
                role = Role(name=name.value, description=desc)
                db.add(role)
            role_map[name.value] = role
        await db.flush()

        perm_map: dict[str, Permission] = {}
        for code, pname, module in PERMISSIONS:
            result = await db.execute(select(Permission).where(Permission.code == code))
            perm = result.scalar_one_or_none()
            if not perm:
                perm = Permission(code=code, name=pname, module=module)
                db.add(perm)
            perm_map[code] = perm
        await db.flush()

        admin_role = role_map[RoleName.SUPER_ADMIN.value]
        for perm in perm_map.values():
            exists = await db.execute(
                select(RolePermission).where(
                    RolePermission.role_id == admin_role.id,
                    RolePermission.permission_id == perm.id,
                )
            )
            if not exists.scalar_one_or_none():
                db.add(RolePermission(role_id=admin_role.id, permission_id=perm.id))

        dept_result = await db.execute(select(Department).where(Department.code == "ENG"))
        dept = dept_result.scalar_one_or_none()
        if not dept:
            dept = Department(
                name="Engineering",
                code="ENG",
                description="Engineering Department",
            )
            db.add(dept)
            await db.flush()

        admin_email = "admin@pathvision.com"
        result = await db.execute(select(User).where(User.email == admin_email))
        admin_user = result.scalar_one_or_none()
        if not admin_user:
            admin_user = User(
                email=admin_email,
                hashed_password=get_password_hash("Admin@123"),
                full_name="Super Admin",
                role_id=admin_role.id,
                is_active=True,
                is_verified=True,
            )
            db.add(admin_user)
            await db.flush()

            db.add(
                Employee(
                    user_id=admin_user.id,
                    employee_code="EMP001",
                    designation="System Administrator",
                    date_of_joining=date.today(),
                    department_id=dept.id,
                )
            )

        hr_email = "hr@pathvision.com"
        hr_result = await db.execute(select(User).where(User.email == hr_email))
        if not hr_result.scalar_one_or_none():
            hr_role = role_map[RoleName.HR_ADMIN.value]
            db.add(
                User(
                    email=hr_email,
                    hashed_password=get_password_hash("Hr@12345"),
                    full_name="HR Admin",
                    role_id=hr_role.id,
                    is_active=True,
                    is_verified=True,
                )
            )

        await db.commit()
        print("Seed completed successfully!")
        print("  Super Admin: admin@pathvision.com / Admin@123")
        print("  HR Admin:    hr@pathvision.com / Hr@12345")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())

