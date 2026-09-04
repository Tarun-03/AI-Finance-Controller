from uuid import UUID

from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.transaction import Transaction
from app.models.payment import Payment
from app.models.settlement import Settlement
from app.models.invoice import Invoice
from app.models.exception import ExceptionRecord
from app.models.finance_policy import FinancePolicy
from app.models.reconciliation import Reconciliation
from app.rag.retriever import retrieve_policies
from mcp.server import MCPServer

mcp = MCPServer(
    "AI Finance Controller",
    version="0.1.0",
)

def get_transaction(transaction_id: str):
    db: Session = SessionLocal()
    try:
        obj = db.get(Transaction, UUID(transaction_id))
        if not obj:
            return {"error": "Transaction not found"}

        return {
            "id": str(obj.id),
            "transaction_id": obj.transaction_id,
            "merchant_id": obj.merchant_id,
            "customer_id": obj.customer_id,
            "amount": obj.amount,
            "currency": obj.currency,
            "status": obj.status.value,
            "transaction_date": obj.transaction_date,
        }
    finally:
        db.close()


def get_payment(transaction_id: str):
    db: Session = SessionLocal()
    try:
        transaction = db.get(Transaction, UUID(transaction_id))

        if not transaction or not transaction.payment:
            return {"error": "Payment not found"}

        obj = transaction.payment

        return {
            "id": str(obj.id),
            "payment_id": obj.payment_id,
            "transaction_id": str(obj.transaction_id),
            "amount": obj.amount,
            "payment_method": obj.payment_method.value,
            "gateway": obj.gateway,
            "status": obj.status.value,
            "payment_timestamp": obj.payment_timestamp,
        }
    finally:
        db.close()


def get_settlement(transaction_id: str):
    db: Session = SessionLocal()
    try:
        transaction = db.get(Transaction, UUID(transaction_id))

        if not transaction or not transaction.settlement:
            return {"error": "Settlement not found"}

        obj = transaction.settlement

        return {
            "id": str(obj.id),
            "settlement_id": obj.settlement_id,
            "transaction_id": str(obj.transaction_id),
            "gross_amount": obj.gross_amount,
            "fee_amount": obj.fee_amount,
            "net_amount": obj.net_amount,
            "status": obj.status.value,
            "settlement_date": obj.settlement_date,
        }
    finally:
        db.close()

def get_invoice(transaction_id: str):
    db: Session = SessionLocal()
    try:
        transaction = db.get(
            Transaction,
            UUID(transaction_id),
        )

        if not transaction or not transaction.invoice:
            return {
                "error": "Invoice not found"
            }

        obj = transaction.invoice

        return {
            "id": str(obj.id),
            "invoice_id": obj.invoice_id,
            "transaction_id": str(obj.transaction_id),
            "invoice_amount": obj.invoice_amount,
            "tax_amount": obj.tax_amount,
            "status": obj.status.value,
            "invoice_date": obj.invoice_date,
            "due_date": obj.due_date,
        }

    finally:
        db.close()


def get_exception(exception_id: str):
    db: Session = SessionLocal()
    try:
        obj = db.get(ExceptionRecord, UUID(exception_id))

        if not obj:
            return {"error": "Exception not found"}

        return {
            "id": str(obj.id),
            "reconciliation_id": str(obj.reconciliation_id),
            "transaction_id": str(obj.transaction_id),
            "exception_type": obj.exception_type.value,
            "severity": obj.severity.value,
            "description": obj.description,
            "expected_value": obj.expected_value,
            "actual_value": obj.actual_value,
            "difference": obj.difference,
        }
    finally:
        db.close()


def get_finance_policy(policy_code: str):
    db: Session = SessionLocal()
    try:
        obj = (
            db.query(FinancePolicy)
            .filter(
                FinancePolicy.policy_code == policy_code,
                FinancePolicy.active.is_(True),
            )
            .first()
        )

        if not obj:
            return {"error": "Finance policy not found"}

        return {
            "id": str(obj.id),
            "policy_code": obj.policy_code,
            "title": obj.title,
            "description": obj.description,
            "category": obj.category,
            "threshold": obj.threshold,
            "action": obj.action,
            "severity": obj.severity,
            "active": obj.active,
        }
    finally:
        db.close()


def get_reconciliation(reconciliation_id: str):
    db: Session = SessionLocal()
    try:
        obj = db.get(Reconciliation, UUID(reconciliation_id))

        if not obj:
            return {"error": "Reconciliation not found"}

        return {
            "id": str(obj.id),
            "transaction_id": str(obj.transaction_id),
            "payment_amount": obj.payment_amount,
            "settlement_amount": obj.settlement_amount,
            "invoice_amount": obj.invoice_amount,
            "payment_settlement_match": obj.payment_settlement_match,
            "payment_invoice_match": obj.payment_invoice_match,
            "status": obj.status.value,
            "difference_amount": obj.difference_amount,
            "resolution_type": obj.resolution_type,
            "confidence_score": obj.confidence_score,
            "reason": obj.reason,
        }
    finally:
        db.close()


def calculate_reconciliation_difference(
    transaction_id: str,
):
    db: Session = SessionLocal()
    try:
        transaction = db.get(Transaction, UUID(transaction_id))

        if not transaction:
            return {"error": "Transaction not found"}

        transaction_amount = transaction.amount

        payment_amount = (
            transaction.payment.amount
            if transaction.payment
            else None
        )

        settlement_amount = (
            transaction.settlement.gross_amount
            if transaction.settlement
            else None
        )

        invoice_amount = (
            transaction.invoice.invoice_amount
            if transaction.invoice
            else None
        )

        differences = {}

        if payment_amount is not None:
            differences["payment_difference"] = (
                payment_amount - transaction_amount
            )

        if settlement_amount is not None:
            differences["settlement_difference"] = (
                settlement_amount - transaction_amount
            )

        if invoice_amount is not None:
            differences["invoice_difference"] = (
                invoice_amount - transaction_amount
            )

        return {
            "transaction_id": transaction_id,
            "transaction_amount": transaction_amount,
            "payment_amount": payment_amount,
            "settlement_amount": settlement_amount,
            "invoice_amount": invoice_amount,
            "differences": differences,
        }
    finally:
        db.close()


def search_finance_policy(query: str):
    db: Session = SessionLocal()
    try:
        return retrieve_policies(db, query)
    finally:
        db.close()

# =====================================================
# MCP TOOL DEFINITIONS
# =====================================================


@mcp.tool()
def transaction_lookup(
    transaction_id: str,
) -> dict:
    """
    Retrieve a transaction using its internal UUID.
    """
    return get_transaction(transaction_id)


@mcp.tool()
def payment_lookup(
    transaction_id: str,
) -> dict:
    """
    Retrieve payment information for a transaction.
    """
    return get_payment(transaction_id)


@mcp.tool()
def settlement_lookup(
    transaction_id: str,
) -> dict:
    """
    Retrieve settlement information for a transaction.
    """
    return get_settlement(transaction_id)


@mcp.tool()
def invoice_lookup(
    transaction_id: str,
) -> dict:
    """
    Retrieve invoice information for a transaction.
    """
    return get_invoice(transaction_id)


@mcp.tool()
def exception_lookup(
    exception_id: str,
) -> dict:
    """
    Retrieve a reconciliation exception.
    """
    return get_exception(exception_id)


@mcp.tool()
def reconciliation_lookup(
    reconciliation_id: str,
) -> dict:
    """
    Retrieve reconciliation evidence.
    """
    return get_reconciliation(
        reconciliation_id
    )


@mcp.tool()
def finance_policy_lookup(
    policy_code: str,
) -> dict:
    """
    Retrieve one active finance policy.
    """
    return get_finance_policy(
        policy_code
    )


@mcp.tool()
def finance_policy_search(
    query: str,
) -> list[dict]:
    """
    Search relevant finance policies
    using the RAG retriever.
    """
    return search_finance_policy(
        query
    )


@mcp.tool()
def reconciliation_difference(
    transaction_id: str,
) -> dict:
    """
    Calculate financial differences between
    transaction, payment, settlement and invoice.
    """
    return calculate_reconciliation_difference(
        transaction_id
    )


if __name__ == "__main__":
    mcp.run()