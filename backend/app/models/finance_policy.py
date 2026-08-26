from decimal import Decimal

from sqlalchemy import Boolean, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class FinancePolicy(BaseModel):
    __tablename__ = "finance_policies"

    policy_code: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
    )

    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    category: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    threshold: Mapped[Decimal | None] = mapped_column(
        Numeric(18, 2),
        nullable=True,
    )

    action: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    severity: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )