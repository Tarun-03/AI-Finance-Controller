import uuid
from uuid import UUID

from sqlalchemy.orm import Session

from app.agents.graph import build_finance_graph
from app.models.enums import (
    AuditAction,
    AuditActor,
    ExceptionStatus,
)
from app.models.exception import ExceptionRecord
from app.services.audit_service import create_audit_log


def investigate_exception(
    db: Session,
    exception_id: UUID,
) -> dict:

    # Verify exception exists before running the agent.
    exception = db.get(
        ExceptionRecord,
        exception_id,
    )

    if exception is None:
        return {
            "exception_id": str(exception_id),
            "error": "Exception not found",
        }

    # Mark exception as being investigated.
    exception.status = ExceptionStatus.INVESTIGATING

    # Unique ID for this agent execution.
    agent_run_id = str(uuid.uuid4())

    graph = build_finance_graph(db)

    result = graph.invoke(
        {
            "exception_id": str(exception_id),
        }
    )

    # Add agent run ID to returned state.
    result["agent_run_id"] = agent_run_id

    # Persist agent decision.
    recommendation = result.get(
        "recommendation"
    )

    confidence = result.get(
        "agent_confidence"
    )

    if recommendation:
        exception.agent_decision = recommendation

    if confidence is not None:
        exception.agent_confidence = confidence

    # Create audit record.
    transaction_id = result.get(
        "transaction_id"
    )

    create_audit_log(
        db,
        action=AuditAction.AGENT_DECISION,
        actor=AuditActor.AGENT,
        transaction_id=(
            UUID(transaction_id)
            if transaction_id
            else None
        ),
        agent_run_id=agent_run_id,
        input_summary=(
            f"Exception {exception_id} investigated."
        ),
        output_summary=(
            f"Recommendation: {recommendation}"
        ),
        reason=result.get(
            "reasoning"
        ),
        confidence=confidence,
    )

    db.commit()

    return result