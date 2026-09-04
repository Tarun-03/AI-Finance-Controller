from decimal import Decimal

from sqlalchemy.orm import Session

from app.models.audit import AuditLog
from app.models.enums import AuditAction, AuditActor


def create_audit_log(
    db: Session,
    *,
    action: AuditAction,
    actor: AuditActor,
    transaction_id=None,
    agent_run_id=None,
    tool_name=None,
    input_summary=None,
    output_summary=None,
    reason=None,
    confidence: Decimal | None = None,
) -> AuditLog:

    log = AuditLog(
        transaction_id=transaction_id,
        agent_run_id=agent_run_id,
        action=action,
        actor=actor,
        tool_name=tool_name,
        input_summary=input_summary,
        output_summary=output_summary,
        reason=reason,
        confidence=confidence,
    )

    db.add(log)
    db.flush()

    return log