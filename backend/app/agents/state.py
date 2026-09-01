from decimal import Decimal
from typing import Literal, TypedDict


class FinanceAgentState(TypedDict, total=False):
    # Identity
    exception_id: str
    transaction_id: str
    reconciliation_id: str

    # Exception facts
    exception_type: str
    severity: str
    description: str

    expected_value: Decimal | None
    actual_value: Decimal | None
    difference: Decimal | None

    # Retrieved finance context
    transaction_reference: str | None
    transaction_amount: Decimal | None
    payment_amount: Decimal | None
    settlement_amount: Decimal | None
    invoice_amount: Decimal | None

    # Later populated by RAG
    retrieved_policies: list[dict]

    # Agent analysis
    risk_score: Decimal | None
    recommendation: Literal[
        "AUTO_RESOLVE",
        "ESCALATE",
        "HUMAN_REVIEW",
    ] | None

    reasoning: str | None

    # Guardrail output
    guardrail_passed: bool
    guardrail_reason: str | None

    # Execution
    final_action: str | None
    requires_human_approval: bool

    # Errors
    error: str | None

    agent_analysis: str | None
    agent_recommendation: str | None
    agent_confidence: Decimal | None