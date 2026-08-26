from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.models.enums import TransactionStatus, TransactionType


class TransactionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    transaction_id: str

    merchant_id: str
    customer_id: str

    amount: Decimal
    currency: str

    transaction_type: TransactionType
    status: TransactionStatus

    transaction_date: datetime
    created_at: datetime
    updated_at: datetime