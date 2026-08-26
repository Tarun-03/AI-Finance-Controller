import uuid
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Enum, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel
from app.models.enums import (
    ExceptionSeverity,
    ExceptionStatus,
    ExceptionType,
)

if TYPE_CHECKING:
    from app.models.reconciliation import Reconciliation
    from app.models.transaction import Transaction


class ExceptionRecord(BaseModel):
    __tablename__ = "exceptions"

    reconciliation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("reconciliations.id"),
        nullable=False,
        index=True,
    )

    transaction_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("transactions.id"),
        nullable=False,
        index=True,
    )

    exception_type: Mapped[ExceptionType] = mapped_column(
        Enum(ExceptionType),
        nullable=False,
    )

    severity: Mapped[ExceptionSeverity] = mapped_column(
        Enum(ExceptionSeverity),
        nullable=False,
        default=ExceptionSeverity.MEDIUM,
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    expected_value: Mapped[Decimal | None] = mapped_column(
        Numeric(18, 2),
        nullable=True,
    )

    actual_value: Mapped[Decimal | None] = mapped_column(
        Numeric(18, 2),
        nullable=True,
    )

    difference: Mapped[Decimal | None] = mapped_column(
        Numeric(18, 2),
        nullable=True,
    )

    status: Mapped[ExceptionStatus] = mapped_column(
        Enum(ExceptionStatus),
        nullable=False,
        default=ExceptionStatus.OPEN,
    )

    agent_decision: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    agent_confidence: Mapped[Decimal | None] = mapped_column(
        Numeric(5, 4),
        nullable=True,
    )

    assigned_to: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    reconciliation: Mapped["Reconciliation"] = relationship(
        back_populates="exceptions",
    )

    transaction: Mapped["Transaction"] = relationship()