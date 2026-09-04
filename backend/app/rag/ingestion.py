from sqlalchemy.orm import Session

from app.models.finance_policy import FinancePolicy

from app.rag.embeddings import (
    build_vocabulary,
    embed_text,
)


def policy_to_text(
    policy: FinancePolicy,
) -> str:
    """
    Convert a finance policy into searchable text.
    """

    return " ".join(
        [
            policy.policy_code or "",
            policy.title or "",
            policy.description or "",
            policy.category or "",
            policy.action or "",
            policy.severity or "",
        ]
    )


def load_policy_documents(
    db: Session,
) -> list[dict]:
    """
    Load all active finance policies.
    """

    policies = (
        db.query(FinancePolicy)
        .filter(
            FinancePolicy.active.is_(True)
        )
        .all()
    )

    documents = []

    for policy in policies:

        text = policy_to_text(policy)

        documents.append(
            {
                "id": str(policy.id),
                "policy_code": policy.policy_code,
                "title": policy.title,
                "description": policy.description,
                "category": policy.category,
                "threshold": policy.threshold,
                "action": policy.action,
                "severity": policy.severity,
                "text": text,
            }
        )

    return documents


def ingest_policies(
    db: Session,
) -> list[dict]:
    """
    Load policies and generate their vectors.
    """

    documents = load_policy_documents(db)

    vocabulary = build_vocabulary(
        [
            document["text"]
            for document in documents
        ]
    )

    for document in documents:

        document["embedding"] = embed_text(
            document["text"],
            vocabulary,
        )

    return documents