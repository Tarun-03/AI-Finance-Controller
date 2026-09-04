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
    try:
        return review_exception(
            db,
            exception_id,
            request,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=404
            if str(exc) == "Exception not found"
            else 400,
            detail=str(exc),
        )