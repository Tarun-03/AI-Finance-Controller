from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.agents.finance_agent import investigate_exception
from app.api.dependencies import get_db
from app.schemas.agent import AgentInvestigationResponse
from app.schemas.review import (
    ExceptionReviewRequest,
    ExceptionReviewResponse,
)
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
    try:
        return investigate_exception(
            db,
            exception_id,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
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
    action = request.action.upper()

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
                "reason": result.get("reason"),
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
                "reason": result.get("reason"),
            }

        if action == "ESCALATE":
            raise ValueError(
                "Manual escalation is not currently implemented."
            )

        raise ValueError(
            "Action must be APPROVE, REJECT, or ESCALATE."
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )