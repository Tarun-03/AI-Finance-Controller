from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.repositories import reconciliation_repository
from app.schemas.reconciliation import ReconciliationResponse
from app.services.reconciliation_service import reconcile_all


router = APIRouter(
    prefix="/reconciliations",
    tags=["Reconciliation"],
)


@router.post(
    "/run",
)
def run_reconciliation(
    db: Session = Depends(get_db),
):
    return reconcile_all(db)


@router.get(
    "",
    response_model=list[ReconciliationResponse],
)
def get_reconciliations(
    db: Session = Depends(get_db),
):
    return reconciliation_repository.get_all_reconciliations(db)


@router.get(
    "/{reconciliation_id}",
    response_model=ReconciliationResponse,
)
def get_reconciliation(
    reconciliation_id: UUID,
    db: Session = Depends(get_db),
):
    reconciliation = (
        reconciliation_repository.get_reconciliation_by_id(
            db,
            reconciliation_id,
        )
    )

    if reconciliation is None:
        raise HTTPException(
            status_code=404,
            detail="Reconciliation not found",
        )

    return reconciliation