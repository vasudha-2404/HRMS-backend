"""Audit logging service."""

import json
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.activity_log import ActivityLog
from app.models.user import User


class AuditService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def log(
        self,
        action: str,
        module: str,
        user: User | None = None,
        entity_type: str | None = None,
        entity_id: UUID | None = None,
        description: str | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> ActivityLog:
        log_entry = ActivityLog(
            user_id=user.id if user else None,
            action=action,
            module=module,
            entity_type=entity_type,
            entity_id=entity_id,
            description=description,
            ip_address=ip_address,
            user_agent=user_agent,
            metadata_json=json.dumps(metadata) if metadata else None,
        )
        self.db.add(log_entry)
        await self.db.flush()
        return log_entry
