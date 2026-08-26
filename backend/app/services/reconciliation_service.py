from decimal import Decimal

from sqlalchemy.orm import Session

from app.models.enums import (
    ExceptionSeverity,
    ExceptionStatus,
    ExceptionType,
    ReconciliationStatus,
)
from app.models.exception import ExceptionRecord
from app.models.reconciliation import Reconciliation
from app.repositories import (
    exception_repository,
    reconciliation_repository,
    transaction_repository,
)


FEE_RATE = Decimal("0.02")
TAX_RATE = Decimal("0.18")


def money(value: Decimal) -> Decimal:
    return value.quantize(Decimal("0.01"))


def reconcile_transaction(
    db: Session,
    transaction,
) -> Reconciliation:

    exceptions: list[ExceptionRecord] = []

    payment = transaction.payment
    settlement = transaction.settlement
    invoice = transaction.invoice

    payment_amount = payment.amount if payment else None
    settlement_amount = (
        settlement.gross_amount
        if settlement
        else None
    )
    invoice_amount = (
        invoice.invoice_amount
        if invoice
        else None
    )

    payment_settlement_match = (
        payment is not None
        and settlement is not None
        and money(payment.amount)
        == money(settlement.gross_amount)
    )

    payment_invoice_match = (
        payment is not None
        and invoice is not None
        and money(
            invoice.invoice_amount
            - invoice.tax_amount
        )
        == money(payment.amount)
    )

    difference_amount = Decimal("0.00")

    # --------------------------------------------------
    # 1. Missing payment
    # --------------------------------------------------

    if payment is None:
        exceptions.append(
            ExceptionRecord(
                reconciliation_id=None,
                transaction_id=transaction.id,
                exception_type=ExceptionType.MISSING_PAYMENT,
                severity=ExceptionSeverity.HIGH,
                description=(
                    "Transaction has no corresponding payment record."
                ),
                expected_value=transaction.amount,
                actual_value=None,
                difference=transaction.amount,
                status=ExceptionStatus.OPEN,
            )
        )

    # --------------------------------------------------
    # 2. Missing settlement
    # --------------------------------------------------

    if settlement is None:
        exceptions.append(
            ExceptionRecord(
                reconciliation_id=None,
                transaction_id=transaction.id,
                exception_type=ExceptionType.MISSING_SETTLEMENT,
                severity=ExceptionSeverity.HIGH,
                description=(
                    "Transaction has no corresponding settlement record."
                ),
                expected_value=transaction.amount,
                actual_value=None,
                difference=transaction.amount,
                status=ExceptionStatus.OPEN,
            )
        )

    # --------------------------------------------------
    # 3. Missing invoice
    # --------------------------------------------------

    if invoice is None:
        exceptions.append(
            ExceptionRecord(
                reconciliation_id=None,
                transaction_id=transaction.id,
                exception_type=ExceptionType.MISSING_INVOICE,
                severity=ExceptionSeverity.MEDIUM,
                description=(
                    "Transaction has no corresponding invoice record."
                ),
                expected_value=transaction.amount,
                actual_value=None,
                difference=transaction.amount,
                status=ExceptionStatus.OPEN,
            )
        )

    # --------------------------------------------------
    # 4. Payment amount mismatch
    # --------------------------------------------------

    if payment is not None:

        difference = money(
            payment.amount - transaction.amount
        )

        if difference != Decimal("0.00"):

            difference_amount = difference

            exceptions.append(
                ExceptionRecord(
                    reconciliation_id=None,
                    transaction_id=transaction.id,
                    exception_type=ExceptionType.AMOUNT_MISMATCH,
                    severity=ExceptionSeverity.HIGH,
                    description=(
                        "Payment amount does not match "
                        "the transaction amount."
                    ),
                    expected_value=transaction.amount,
                    actual_value=payment.amount,
                    difference=difference,
                    status=ExceptionStatus.OPEN,
                )
            )

    # --------------------------------------------------
    # 5. Settlement gross amount
    # --------------------------------------------------

    if settlement is not None:

        difference = money(
            settlement.gross_amount
            - transaction.amount
        )

        if difference != Decimal("0.00"):

            difference_amount = difference

            exceptions.append(
                ExceptionRecord(
                    reconciliation_id=None,
                    transaction_id=transaction.id,
                    exception_type=ExceptionType.AMOUNT_MISMATCH,
                    severity=ExceptionSeverity.HIGH,
                    description=(
                        "Settlement gross amount does not "
                        "match the transaction amount."
                    ),
                    expected_value=transaction.amount,
                    actual_value=settlement.gross_amount,
                    difference=difference,
                    status=ExceptionStatus.OPEN,
                )
            )

    # --------------------------------------------------
    # 6. Fee validation
    # --------------------------------------------------

    if settlement is not None:

        expected_fee = money(
            settlement.gross_amount * FEE_RATE
        )

        fee_difference = money(
            settlement.fee_amount - expected_fee
        )

        if fee_difference != Decimal("0.00"):

            difference_amount = fee_difference

            exceptions.append(
                ExceptionRecord(
                    reconciliation_id=None,
                    transaction_id=transaction.id,
                    exception_type=ExceptionType.FEE_MISMATCH,
                    severity=ExceptionSeverity.MEDIUM,
                    description=(
                        "Settlement processing fee differs "
                        "from the expected fee rate."
                    ),
                    expected_value=expected_fee,
                    actual_value=settlement.fee_amount,
                    difference=fee_difference,
                    status=ExceptionStatus.OPEN,
                )
            )

    # --------------------------------------------------
    # 7. Payment status
    # --------------------------------------------------

    if payment is not None:

        if (
            transaction.status.value
            != payment.status.value
        ):
            exceptions.append(
                ExceptionRecord(
                    reconciliation_id=None,
                    transaction_id=transaction.id,
                    exception_type=ExceptionType.STATUS_MISMATCH,
                    severity=ExceptionSeverity.HIGH,
                    description=(
                        "Transaction status does not "
                        "match payment status."
                    ),
                    expected_value=None,
                    actual_value=None,
                    difference=None,
                    status=ExceptionStatus.OPEN,
                )
            )

    # --------------------------------------------------
    # Determine reconciliation status
    # --------------------------------------------------

    if exceptions:
        status = ReconciliationStatus.MISMATCH
        resolution_type = "REVIEW_REQUIRED"
        confidence = Decimal("1.0000")

    else:
        status = ReconciliationStatus.MATCHED
        resolution_type = "AUTO_MATCH"
        confidence = Decimal("1.0000")

    reason = (
        "Transaction successfully reconciled."
        if not exceptions
        else f"{len(exceptions)} reconciliation issue(s) detected."
    )

    reconciliation = Reconciliation(
        transaction_id=transaction.id,
        payment_amount=payment_amount,
        settlement_amount=settlement_amount,
        invoice_amount=invoice_amount,
        payment_settlement_match=payment_settlement_match,
        payment_invoice_match=payment_invoice_match,
        status=status,
        difference_amount=difference_amount,
        resolution_type=resolution_type,
        confidence_score=confidence,
        reason=reason,
    )

    reconciliation_repository.create_reconciliation(
        db,
        reconciliation,
    )

    # Reconciliation ID is now available after flush
    for exception in exceptions:
        exception.reconciliation_id = reconciliation.id

        exception_repository.create_exception(
            db,
            exception,
        )

    return reconciliation


def reconcile_all(
    db: Session,
) -> dict:

    # Clear previous generated reconciliation results.
    exception_repository.clear_exceptions(db)
    reconciliation_repository.clear_reconciliations(db)

    transactions = (
        transaction_repository.get_all_transactions(db)
    )

    matched = 0
    mismatched = 0
    total_exceptions = 0

    for transaction in transactions:

        reconciliation = reconcile_transaction(
            db,
            transaction,
        )

        if (
            reconciliation.status
            == ReconciliationStatus.MATCHED
        ):
            matched += 1
        else:
            mismatched += 1

            # Count exceptions created for this transaction.
            total_exceptions += len(
                reconciliation.exceptions
            )

    db.commit()

    return {
        "total_transactions": len(transactions),
        "matched": matched,
        "mismatched": mismatched,
        "total_exceptions": total_exceptions,
    }