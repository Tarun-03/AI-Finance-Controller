from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.agents.finance_agent import investigate_exception
from app.api.dependencies import get_db
from app.schemas.agent import AgentInvestigationResponse


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