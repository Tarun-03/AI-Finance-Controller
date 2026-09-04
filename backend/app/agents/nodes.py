from decimal import Decimal

from sqlalchemy.orm import Session

from app.agents.state import FinanceAgentState
from app.models.exception import ExceptionRecord
from app.models.transaction import Transaction
from app.services.llm_service import LLMService
from app.rag.retriever import retrieve_policies


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

    # Missing financial records must never be
    # automatically resolved.
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

    # Small differences can potentially be
    # automatically resolved.
    if difference <= AUTO_RESOLVE_LIMIT:
        return {
            "recommendation": "AUTO_RESOLVE",
            "reasoning": (
                "Difference is within the current "
                "auto-resolution threshold."
            ),
            "requires_human_approval": False,
        }

    # Moderate differences require human review.
    if difference <= HUMAN_REVIEW_LIMIT:
        return {
            "recommendation": "HUMAN_REVIEW",
            "reasoning": (
                "Difference exceeds auto-resolution "
                "threshold but remains within manual-review range."
            ),
            "requires_human_approval": True,
        }

    # Large differences must be escalated.
    return {
        "recommendation": "ESCALATE",
        "reasoning": (
            "Difference exceeds the permitted "
            "manual-review threshold."
        ),
        "requires_human_approval": True,
    }

def llm_investigation_node(
    state: FinanceAgentState,
) -> FinanceAgentState:

    if state.get("error"):
        return {}

    context = {
        "exception_type": state["exception_type"],
        "severity": state["severity"],
        "description": state["description"],

        "expected_value": state.get("expected_value"),
        "actual_value": state.get("actual_value"),
        "difference": state.get("difference"),

        "transaction_amount": state.get(
            "transaction_amount"
        ),

        "payment_amount": state.get(
            "payment_amount"
        ),

        "settlement_amount": state.get(
            "settlement_amount"
        ),

        "invoice_amount": state.get(
            "invoice_amount"
        ),

        "recommendation": state.get(
            "recommendation"
        ),

        "retrieved_policies": state.get(
            "retrieved_policies",
            [],
),
    }

    service = LLMService()

    result = service.analyze_exception(
        context
    )

    return {
        "agent_analysis": {
            "analysis": result["analysis"],
            "recommended_action": result[
                "recommended_action"
            ],
            "confidence": result[
                "confidence"
            ],
        },

        "agent_recommendation": result[
            "recommended_action"
        ],

        "agent_confidence": result[
            "confidence"
        ],
    }



def guardrail_node(
    state: FinanceAgentState,
) -> FinanceAgentState:

    # Deterministic recommendation is authoritative.
    recommendation = state.get(
        "recommendation"
    )

    # LLM recommendation is advisory only.
    llm_recommendation = state.get(
        "agent_recommendation"
    )

    difference = abs(
        state.get("difference")
        or Decimal("0.00")
    )

    # --------------------------------------------------
    # AUTO-RESOLUTION GUARDRAILS
    # --------------------------------------------------

    if recommendation == "AUTO_RESOLVE":

        # Never automatically resolve a large
        # financial discrepancy.
        if difference > AUTO_RESOLVE_LIMIT:
            return {
                "guardrail_passed": False,
                "guardrail_reason": (
                    "Auto-resolution blocked because "
                    "difference exceeds the safety threshold."
                ),
            }

        # Missing records require investigation.
        if state["exception_type"].startswith(
            "MISSING_"
        ):
            return {
                "guardrail_passed": False,
                "guardrail_reason": (
                    "Missing financial records cannot "
                    "be auto-resolved."
                ),
            }

    # --------------------------------------------------
    # FINAL GUARDRAIL RESULT
    # --------------------------------------------------

    return {
        "guardrail_passed": True,
        "guardrail_reason": (
            "Deterministic finance rules approved "
            "the proposed action. "
            f"LLM recommendation: "
            f"{llm_recommendation or 'N/A'}."
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

def retrieve_policies_node(
    state: FinanceAgentState,
    db: Session,
) -> FinanceAgentState:

    if state.get("error"):
        return {}

    query = " ".join(
        [
            state.get("exception_type", ""),
            state.get("severity", ""),
            state.get("description", ""),
            f"difference {state.get('difference', '')}",
        ]
    )

    policies = retrieve_policies(
        db,
        query,
        top_k=3,
    )

    return {
        "retrieved_policies": policies,
    }

def mcp_evidence_node(
    state: FinanceAgentState,
) -> FinanceAgentState:

    if state.get("error"):
        return {}

    from app.mcp.server import (
        transaction_lookup,
        payment_lookup,
        settlement_lookup,
        invoice_lookup,
        exception_lookup,
        reconciliation_lookup,
        reconciliation_difference,
    )

    transaction_id = state["transaction_id"]
    exception_id = state["exception_id"]
    reconciliation_id = state["reconciliation_id"]

    transaction = transaction_lookup(transaction_id)
    payment = payment_lookup(transaction_id)
    settlement = settlement_lookup(transaction_id)
    invoice = invoice_lookup(transaction_id)
    exception = exception_lookup(exception_id)
    reconciliation = reconciliation_lookup(
        reconciliation_id
    )
    differences = reconciliation_difference(
        transaction_id
    )

    return {
        "mcp_transaction": transaction,
        "mcp_payment": payment,
        "mcp_settlement": settlement,
        "mcp_invoice": invoice,
        "mcp_exception": exception,
        "mcp_reconciliation": reconciliation,
        "mcp_differences": differences,
    }