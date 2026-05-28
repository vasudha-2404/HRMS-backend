"""Create all database tables (development bootstrap). Prefer Alembic in production."""

import asyncio

from app.core.database import Base, engine
from app.models import *  # noqa: F401,F403


async def create_tables() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("All tables created successfully.")


if __name__ == "__main__":
    asyncio.run(create_tables())

