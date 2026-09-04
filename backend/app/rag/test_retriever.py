from app.db.session import SessionLocal
from app.rag.retriever import retrieve_policies


db = SessionLocal()

try:
    results = retrieve_policies(
        db,
        query=(
            "AMOUNT_MISMATCH payment difference "
            "manual review threshold"
        ),
        top_k=3,
    )

    print("\nRetrieved policies:\n")

    for policy in results:
        print(
            f"{policy['policy_code']} "
            f"| similarity={policy['similarity']}"
        )

        print(
            f"Title: {policy['title']}"
        )

        print(
            f"Description: {policy['description']}"
        )

        print()

finally:
    db.close()