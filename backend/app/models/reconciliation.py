import uuid
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Enum, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel
from app.models.enums import ReconciliationStatus

if TYPE_CHECKING:
    from app.models.exception import ExceptionRecord
    from app.models.transaction import Transaction


class Reconciliation(BaseModel):
    __tablename__ = "reconciliations"

    transaction_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("transactions.id"),
        unique=True,
        nullable=False,
        index=True,
    )

    payment_amount: Mapped[Decimal | None] = mapped_column(
        Numeric(18, 2),
        nullable=True,
    )

    settlement_amount: Mapped[Decimal | None] = mapped_column(
        Numeric(18, 2),
        nullable=True,
    )

    invoice_amount: Mapped[Decimal | None] = mapped_column(
        Numeric(18, 2),
        nullable=True,
    )

    payment_settlement_match: Mapped[bool] = mapped_column(
        nullable=False,
        default=False,
    )

    payment_invoice_match: Mapped[bool] = mapped_column(
        nullable=False,
        default=False,
    )

    status: Mapped[ReconciliationStatus] = mapped_column(
        Enum(ReconciliationStatus),
        nullable=False,
        default=ReconciliationStatus.PENDING,
    )

    difference_amount: Mapped[Decimal] = mapped_column(
        Numeric(18, 2),
        nullable=False,
        default=Decimal("0.00"),
    )

    resolution_type: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    confidence_score: Mapped[Decimal | None] = mapped_column(
        Numeric(5, 4),
        nullable=True,
    )

    reason: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    transaction: Mapped["Transaction"] = relationship(
        back_populates="reconciliation",
    )

    exceptions: Mapped[list["ExceptionRecord"]] = relationship(
        back_populates="reconciliation",
        cascade="all, delete-orphan",
    )