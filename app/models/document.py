"""Document storage metadata model."""

import uuid
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Enum, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import BaseModel
from app.utils.enums import DocumentType

if TYPE_CHECKING:
    from app.models.employee import Employee
    from app.models.user import User


class Document(BaseModel, Base):
    __tablename__ = "documents"

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    file_url: Mapped[str] = mapped_column(String(500), nullable=False)
    file_type: Mapped[str] = mapped_column(String(50), nullable=False)
    document_type: Mapped[DocumentType] = mapped_column(
        Enum(
            DocumentType,
            name="document_type_enum",
            create_type=False,
            values_callable=lambda enum: [e.value for e in enum],
        ),
        default=DocumentType.OTHER,
        nullable=False,
    )
    file_size: Mapped[int | None] = mapped_column(Integer, nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    uploaded_by_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    employee_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("employees.id"), nullable=True
    )
    applicant_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("applicants.id"), nullable=True
    )

    uploaded_by: Mapped["User"] = relationship("User")
    employee: Mapped[Optional["Employee"]] = relationship("Employee")
