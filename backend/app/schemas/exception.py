from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.models.enums import (
    ExceptionSeverity,
    ExceptionStatus,
    ExceptionType,
)


class ExceptionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    reconciliation_id: UUID
    transaction_id: UUID

    exception_type: ExceptionType
    severity: ExceptionSeverity

    description: str

    expected_value: Decimal | None
    actual_value: Decimal | None
    difference: Decimal | None

    status: ExceptionStatus

    agent_decision: str | None
    agent_confidence: Decimal | None
    assigned_to: str | None