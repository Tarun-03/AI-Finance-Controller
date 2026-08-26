from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.repositories import transaction_repository
from app.schemas.transaction import TransactionResponse


router = APIRouter(
    prefix="/transactions",
    tags=["Transactions"],
)


@router.get(
    "",
    response_model=list[TransactionResponse],
)
def get_transactions(
    db: Session = Depends(get_db),
):
    return transaction_repository.get_all_transactions(db)


@router.get(
    "/{transaction_id}",
    response_model=TransactionResponse,
)
def get_transaction(
    transaction_id: str,
    db: Session = Depends(get_db),
):
    transaction = (
        transaction_repository.get_transaction_by_id(
            db,
            transaction_id,
        )
    )

    if transaction is None:
        raise HTTPException(
            status_code=404,
            detail="Transaction not found",
        )

    return transaction