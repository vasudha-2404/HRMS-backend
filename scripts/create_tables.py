"""Create all database tables (development bootstrap). Prefer Alembic in production."""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import Enum as SAEnum, text

from app.core.config import settings
from app.core.database import Base, engine
from app.models import *  # noqa: F401, F403


async def ensure_postgres_enums() -> None:
    """Create PostgreSQL enum types if missing (idempotent)."""
    enum_defs: dict[str, list[str]] = {}
    for table in Base.metadata.tables.values():
        for column in table.columns:
            if isinstance(column.type, SAEnum) and getattr(column.type, "name", None):
                enum_defs[column.type.name] = list(column.type.enums)

    if not enum_defs:
        return

    async with engine.begin() as conn:
        for enum_name, values in enum_defs.items():
            values_sql = ", ".join(f"'{v}'" for v in values)
            await conn.execute(
                text(
                    f"""
                    DO $$
                    BEGIN
                        IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = '{enum_name}') THEN
                            CREATE TYPE {enum_name} AS ENUM ({values_sql});
                        END IF;
                    END
                    $$;
                    """
                )
            )
            for value in values:
                await conn.execute(
                    text(
                        f"""
                        DO $$
                        BEGIN
                            IF EXISTS (SELECT 1 FROM pg_type WHERE typname = '{enum_name}')
                               AND NOT EXISTS (
                                   SELECT 1
                                   FROM pg_enum e
                                   JOIN pg_type t ON t.oid = e.enumtypid
                                   WHERE t.typname = '{enum_name}' AND e.enumlabel = '{value}'
                               ) THEN
                                ALTER TYPE {enum_name} ADD VALUE '{value}';
                            END IF;
                        END
                        $$;
                        """
                    )
                )


async def create_tables() -> None:
    await ensure_postgres_enums()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("All tables created successfully.")


if __name__ == "__main__":
    asyncio.run(create_tables())
