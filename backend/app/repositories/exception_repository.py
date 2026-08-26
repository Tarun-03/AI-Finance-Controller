from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models.exception import ExceptionRecord


def clear_exceptions(db: Session) -> None:
    db.execute(delete(ExceptionRecord))


def create_exception(
    db: Session,
    exception: ExceptionRecord,
) -> ExceptionRecord:
    db.add(exception)
    db.flush()

    return exception


def get_all_exceptions(
    db: Session,
) -> list[ExceptionRecord]:
    statement = select(ExceptionRecord).order_by(
        ExceptionRecord.created_at
    )

    return list(db.scalars(statement).all())


def get_open_exceptions(
    db: Session,
) -> list[ExceptionRecord]:
    statement = select(ExceptionRecord).where(
        ExceptionRecord.status == "OPEN"
    )

    return list(db.scalars(statement).all())