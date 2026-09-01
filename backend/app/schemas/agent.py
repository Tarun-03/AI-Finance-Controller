from decimal import Decimal

from pydantic import BaseModel, Field


class AgentAnalysis(BaseModel):
    analysis: str

    recommended_action: str

    confidence: Decimal = Field(
        ge=0,
        le=1,
    )


class AgentInvestigationResponse(BaseModel):
    exception_id: str

    transaction_id: str | None = None
    transaction_reference: str | None = None

    exception_type: str | None = None
    severity: str | None = None

    expected_value: Decimal | None = None
    actual_value: Decimal | None = None
    difference: Decimal | None = None

    risk_score: Decimal | None = None

    recommendation: str | None = None

    reasoning: str | None = None

    agent_analysis: AgentAnalysis | None = None

    guardrail_passed: bool | None = None
    guardrail_reason: str | None = None

    requires_human_approval: bool = False

    final_action: str | None = None

    error: str | None = None