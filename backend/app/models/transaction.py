import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, Enum, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel
from app.models.enums import TransactionStatus, TransactionType

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.payment import Payment

from app.models.invoice import Invoice

invoice: Mapped["Invoice | None"] = relationship(
    back_populates="transaction",
    uselist=False,
)

from app.models.settlement import Settlement

settlement: Mapped["Settlement | None"] = relationship(
    back_populates="transaction",
    uselist=False,
)

class Transaction(BaseModel):
    __tablename__ = "transactions"

    transaction_id: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
    )

    merchant_id: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )

    customer_id: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )

    amount: Mapped[Decimal] = mapped_column(
        Numeric(18, 2),
        nullable=False,
    )

    currency: Mapped[str] = mapped_column(
        String(3),
        nullable=False,
        default="INR",
    )

    transaction_type: Mapped[TransactionType] = mapped_column(
        Enum(TransactionType),
        nullable=False,
    )

    status: Mapped[TransactionStatus] = mapped_column(
        Enum(TransactionStatus),
        nullable=False,
        default=TransactionStatus.PENDING,
    )

    transaction_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    payment: Mapped["Payment | None"] = relationship(
        back_populates="transaction",
        uselist=False,
    )