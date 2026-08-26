from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.transaction import Transaction


def get_all_transactions(db: Session) -> list[Transaction]:
    statement = (
        select(Transaction)
        .options(
            selectinload(Transaction.payment),
            selectinload(Transaction.settlement),
            selectinload(Transaction.invoice),
        )
        .order_by(Transaction.transaction_id)
    )

    return list(db.scalars(statement).all())


def get_transaction_by_id(
    db: Session,
    transaction_id: str,
) -> Transaction | None:
    statement = (
        select(Transaction)
        .options(
            selectinload(Transaction.payment),
            selectinload(Transaction.settlement),
            selectinload(Transaction.invoice),
        )
        .where(Transaction.transaction_id == transaction_id)
    )

    return db.scalar(statement)