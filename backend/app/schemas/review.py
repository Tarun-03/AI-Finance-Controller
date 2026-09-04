from pydantic import BaseModel, Field


class ExceptionReviewRequest(BaseModel):
    action: str = Field(
        description="APPROVE, REJECT, or ESCALATE"
    )

    reason: str | None = None

    reviewer: str = "finance_user"


class ExceptionReviewResponse(BaseModel):
    exception_id: str
    status: str
    action: str
    reviewer: str
    reason: str | None = None