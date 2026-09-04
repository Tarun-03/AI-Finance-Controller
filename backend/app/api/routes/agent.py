from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.agents.finance_agent import investigate_exception
from app.api.dependencies import get_db
from app.models.enums import (
    AuditAction,
    AuditActor,
    ExceptionStatus,
)
from app.models.exception import ExceptionRecord
from app.schemas.agent import AgentInvestigationResponse
from app.schemas.review import (
    ExceptionReviewRequest,
    ExceptionReviewResponse,
)
from app.services.audit_service import create_audit_log
from app.services.exception_service import (
    approve_exception,
    reject_exception,
)


router = APIRouter(
    prefix="/agent",
    tags=["Agentic Finance"],
)


@router.post(
    "/exceptions/{exception_id}/investigate",
    response_model=AgentInvestigationResponse,
)
def investigate_finance_exception(
    exception_id: UUID,
    db: Session = Depends(get_db),
):
    return investigate_exception(
        db,
        exception_id,
    )


@router.post(
    "/exceptions/{exception_id}/review",
    response_model=ExceptionReviewResponse,
)
def review_finance_exception(
    exception_id: UUID,
    request: ExceptionReviewRequest,
    db: Session = Depends(get_db),
):
    action = request.action.upper().strip()

    if action not in {"APPROVE", "REJECT", "ESCALATE"}:
        raise HTTPException(
            status_code=400,
            detail="Action must be APPROVE, REJECT, or ESCALATE",
        )

    try:
        if action == "APPROVE":
            result = approve_exception(
                db,
                exception_id,
                request.reason,
            )

            return {
                "exception_id": result["exception_id"],
                "status": result["status"],
                "action": "APPROVE",
                "reviewer": request.reviewer,
                "reason": result["reason"],
            }

        if action == "REJECT":
            result = reject_exception(
                db,
                exception_id,
                request.reason,
            )

            return {
                "exception_id": result["exception_id"],
                "status": result["status"],
                "action": "REJECT",
                "reviewer": request.reviewer,
                "reason": result["reason"],
            }

        exception = db.get(
            ExceptionRecord,
            exception_id,
        )

        if exception is None:
            raise ValueError("Exception not found")

        if exception.status != ExceptionStatus.INVESTIGATING:
            raise ValueError(
                f"Exception cannot be escalated "
                f"from status {exception.status.value}"
            )

        exception.status = ExceptionStatus.ESCALATED

        create_audit_log(
            db,
            action=AuditAction.MANUAL_OVERRIDE,
            actor=AuditActor.USER,
            transaction_id=exception.transaction_id,
            input_summary=(
                f"Escalate exception {exception_id}"
            ),
            output_summary=(
                "Exception status changed to ESCALATED."
            ),
            reason=(
                request.reason
                or "Human escalated the exception."
            ),
        )

        db.commit()

        return {
            "exception_id": str(exception.id),
            "status": exception.status.value,
            "action": "ESCALATE",
            "reviewer": request.reviewer,
            "reason": request.reason,
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=404
            if str(exc) == "Exception not found"
            else 400,
            detail=str(exc),
        )
