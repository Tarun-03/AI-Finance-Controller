from sqlalchemy import delete, select
from sqlalchemy.orm import Session
from uuid import UUID

from app.models.reconciliation import Reconciliation


def clear_reconciliations(db: Session) -> None:
    db.execute(delete(Reconciliation))


def create_reconciliation(
    db: Session,
    reconciliation: Reconciliation,
) -> Reconciliation:
    db.add(reconciliation)
    db.flush()

    return reconciliation


def get_reconciliation_by_transaction_id(
    db: Session,
    transaction_id,
):
    statement = select(Reconciliation).where(
        Reconciliation.transaction_id == transaction_id
    )

    return db.scalar(statement)


def get_all_reconciliations(
    db: Session,
) -> list[Reconciliation]:
    statement = select(Reconciliation).order_by(
        Reconciliation.created_at
    )

    return list(db.scalars(statement).all())

def get_reconciliation_by_id(
    db: Session,
    reconciliation_id: UUID,
) -> Reconciliation | None:
    statement = select(Reconciliation).where(
        Reconciliation.id == reconciliation_id
    )

    return db.scalar(statement)