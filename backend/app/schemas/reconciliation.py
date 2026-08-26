from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.models.enums import ReconciliationStatus


class ReconciliationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    transaction_id: UUID

    payment_amount: Decimal | None
    settlement_amount: Decimal | None
    invoice_amount: Decimal | None

    payment_settlement_match: bool
    payment_invoice_match: bool

    status: ReconciliationStatus
    difference_amount: Decimal

    resolution_type: str | None
    confidence_score: Decimal | None
    reason: str | None