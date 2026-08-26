from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.repositories import exception_repository
from app.schemas.exception import ExceptionResponse


router = APIRouter(
    prefix="/exceptions",
    tags=["Exceptions"],
)


@router.get(
    "",
    response_model=list[ExceptionResponse],
)
def get_exceptions(
    db: Session = Depends(get_db),
):
    return exception_repository.get_all_exceptions(db)


@router.get(
    "/open",
    response_model=list[ExceptionResponse],
)
def get_open_exceptions(
    db: Session = Depends(get_db),
):
    return exception_repository.get_open_exceptions(db)


@router.get(
    "/{exception_id}",
    response_model=ExceptionResponse,
)
def get_exception(
    exception_id: UUID,
    db: Session = Depends(get_db),
):
    exception = exception_repository.get_exception_by_id(
        db,
        exception_id,
    )

    if exception is None:
        raise HTTPException(
            status_code=404,
            detail="Exception not found",
        )

    return exception