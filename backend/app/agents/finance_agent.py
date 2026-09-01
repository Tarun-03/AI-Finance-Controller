from uuid import UUID

from sqlalchemy.orm import Session

from app.agents.graph import build_finance_graph


def investigate_exception(
    db: Session,
    exception_id: UUID,
) -> dict:

    graph = build_finance_graph(db)

    result = graph.invoke(
        {
            "exception_id": str(
                exception_id
            ),
        }
    )

    return result