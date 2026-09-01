from decimal import Decimal

from sqlalchemy.orm import Session

from app.agents.state import FinanceAgentState
from app.models.exception import ExceptionRecord
from app.models.transaction import Transaction


AUTO_RESOLVE_LIMIT = Decimal("100.00")
HUMAN_REVIEW_LIMIT = Decimal("1000.00")


def load_context_node(
    state: FinanceAgentState,
    db: Session,
) -> FinanceAgentState:

    exception = db.get(
        ExceptionRecord,
        state["exception_id"],
    )

    if exception is None:
        return {
            "error": "Exception not found",
        }

    transaction = db.get(
        Transaction,
        exception.transaction_id,
    )

    if transaction is None:
        return {
            "error": "Transaction not found",
        }

    return {
        "transaction_id": str(transaction.id),
        "reconciliation_id": str(exception.reconciliation_id),

        "exception_type": exception.exception_type.value,
        "severity": exception.severity.value,
        "description": exception.description,

        "expected_value": exception.expected_value,
        "actual_value": exception.actual_value,
        "difference": exception.difference,

        "transaction_reference": transaction.transaction_id,
        "transaction_amount": transaction.amount,

        "payment_amount": (
            transaction.payment.amount
            if transaction.payment
            else None
        ),

        "settlement_amount": (
            transaction.settlement.gross_amount
            if transaction.settlement
            else None
        ),

        "invoice_amount": (
            transaction.invoice.invoice_amount
            if transaction.invoice
            else None
        ),

        "retrieved_policies": [],
    }


def assess_risk_node(
    state: FinanceAgentState,
) -> FinanceAgentState:

    if state.get("error"):
        return {}

    difference = abs(
        state.get("difference")
        or Decimal("0.00")
    )

    severity = state["severity"]

    score = Decimal("0.20")

    if severity == "MEDIUM":
        score = Decimal("0.45")

    elif severity == "HIGH":
        score = Decimal("0.75")

    elif severity == "CRITICAL":
        score = Decimal("1.00")

    if difference > HUMAN_REVIEW_LIMIT:
        score = max(
            score,
            Decimal("0.90"),
        )

    elif difference > AUTO_RESOLVE_LIMIT:
        score = max(
            score,
            Decimal("0.60"),
        )

    return {
        "risk_score": score,
    }


def decide_action_node(
    state: FinanceAgentState,
) -> FinanceAgentState:

    if state.get("error"):
        return {}

    exception_type = state["exception_type"]

    difference = abs(
        state.get("difference")
        or Decimal("0.00")
    )

    # Missing records should never be auto-resolved.
    if exception_type in {
        "MISSING_PAYMENT",
        "MISSING_SETTLEMENT",
        "MISSING_INVOICE",
    }:
        return {
            "recommendation": "ESCALATE",
            "reasoning": (
                "Required financial evidence is missing."
            ),
            "requires_human_approval": True,
        }

    if difference <= AUTO_RESOLVE_LIMIT:
        return {
            "recommendation": "AUTO_RESOLVE",
            "reasoning": (
                "Difference is within the current "
                "auto-resolution threshold."
            ),
            "requires_human_approval": False,
        }

    if difference <= HUMAN_REVIEW_LIMIT:
        return {
            "recommendation": "HUMAN_REVIEW",
            "reasoning": (
                "Difference exceeds auto-resolution "
                "threshold but remains within manual-review range."
            ),
            "requires_human_approval": True,
        }

    return {
        "recommendation": "ESCALATE",
        "reasoning": (
            "Difference exceeds the permitted "
            "manual-review threshold."
        ),
        "requires_human_approval": True,
    }


def guardrail_node(
    state: FinanceAgentState,
) -> FinanceAgentState:

    recommendation = state.get(
        "recommendation"
    )

    difference = abs(
        state.get("difference")
        or Decimal("0.00")
    )

    if recommendation == "AUTO_RESOLVE":

        if difference > AUTO_RESOLVE_LIMIT:
            return {
                "guardrail_passed": False,
                "guardrail_reason": (
                    "Auto-resolution blocked because "
                    "difference exceeds safety threshold."
                ),
            }

        if state["exception_type"].startswith("MISSING_"):
            return {
                "guardrail_passed": False,
                "guardrail_reason": (
                    "Missing financial records cannot "
                    "be auto-resolved."
                ),
            }

    return {
        "guardrail_passed": True,
        "guardrail_reason": (
            "Action satisfies current finance guardrails."
        ),
    }


def resolve_node(
    state: FinanceAgentState,
) -> FinanceAgentState:

    return {
        "final_action": "RESOLVED",
    }


def escalate_node(
    state: FinanceAgentState,
) -> FinanceAgentState:

    return {
        "final_action": "ESCALATED",
        "requires_human_approval": True,
    }


def human_review_node(
    state: FinanceAgentState,
) -> FinanceAgentState:

    return {
        "final_action": "PENDING_HUMAN_REVIEW",
        "requires_human_approval": True,
    }


def failed_node(
    state: FinanceAgentState,
) -> FinanceAgentState:

    return {
        "final_action": "FAILED",
    }