import uuid
from decimal import Decimal
from typing import TYPE_CHECKING
from datetime import datetime
from sqlalchemy import DateTime, Enum, ForeignKey, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel
from app.models.enums import AuditAction, AuditActor

if TYPE_CHECKING:
    from app.models.transaction import Transaction


class AuditLog(BaseModel):
    __tablename__ = "audit_logs"

    transaction_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("transactions.id"),
        nullable=True,
        index=True,
    )

    agent_run_id: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        index=True,
    )

    action: Mapped[AuditAction] = mapped_column(
        Enum(AuditAction),
        nullable=False,
    )

    actor: Mapped[AuditActor] = mapped_column(
        Enum(AuditActor),
        nullable=False,
    )

    tool_name: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    input_summary: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    output_summary: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    reason: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    confidence: Mapped[Decimal | None] = mapped_column(
        Numeric(5, 4),
        nullable=True,
    )

    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    transaction: Mapped["Transaction | None"] = relationship()