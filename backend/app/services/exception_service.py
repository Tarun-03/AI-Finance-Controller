from uuid import UUID

from sqlalchemy.orm import Session

from app.models.enums import (
    AuditAction,
    AuditActor,
    ExceptionStatus,
)
from app.models.exception import ExceptionRecord
from app.services.audit_service import create_audit_log


def approve_exception(
    db: Session,
    exception_id: UUID,
    reason: str | None = None,
) -> dict:

    exception = db.get(
        ExceptionRecord,
        exception_id,
    )

    if exception is None:
        raise ValueError(
            "Exception not found"
        )

    if exception.status != ExceptionStatus.INVESTIGATING:
        raise ValueError(
            f"Exception cannot be approved "
            f"from status {exception.status.value}"
        )

    exception.status = ExceptionStatus.RESOLVED

    create_audit_log(
        db,
        action=AuditAction.MANUAL_OVERRIDE,
        actor=AuditActor.USER,
        transaction_id=exception.transaction_id,
        input_summary=(
            f"Approve exception {exception_id}"
        ),
        output_summary="Exception resolved.",
        reason=reason or "Human approved agent decision.",
    )

    create_audit_log(
        db,
        action=AuditAction.EXCEPTION_RESOLVED,
        actor=AuditActor.USER,
        transaction_id=exception.transaction_id,
        input_summary=(
            f"Exception {exception_id}"
        ),
        output_summary="Exception status changed to RESOLVED.",
        reason=reason or "Human approval.",
    )

    db.commit()

    return {
        "exception_id": str(exception.id),
        "status": exception.status.value,
        "decision": "APPROVED",
        "reason": reason,
    }


def reject_exception(
    db: Session,
    exception_id: UUID,
    reason: str | None = None,
) -> dict:

    exception = db.get(
        ExceptionRecord,
        exception_id,
    )

    if exception is None:
        raise ValueError(
            "Exception not found"
        )

    if exception.status != ExceptionStatus.INVESTIGATING:
        raise ValueError(
            f"Exception cannot be rejected "
            f"from status {exception.status.value}"
        )

    exception.status = ExceptionStatus.REJECTED

    create_audit_log(
        db,
        action=AuditAction.MANUAL_OVERRIDE,
        actor=AuditActor.USER,
        transaction_id=exception.transaction_id,
        input_summary=(
            f"Reject exception {exception_id}"
        ),
        output_summary="Exception rejected.",
        reason=reason or "Human rejected agent decision.",
    )

    db.commit()

    return {
        "exception_id": str(exception.id),
        "status": exception.status.value,
        "decision": "REJECTED",
        "reason": reason,
    }