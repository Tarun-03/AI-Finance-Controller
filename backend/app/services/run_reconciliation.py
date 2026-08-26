from app.db.session import SessionLocal
from app.services.reconciliation_service import reconcile_all


def main() -> None:
    db = SessionLocal()

    try:
        result = reconcile_all(db)

        print("\nReconciliation completed")
        print("------------------------")
        print(
            f"Transactions : {result['total_transactions']}"
        )
        print(
            f"Matched      : {result['matched']}"
        )
        print(
            f"Mismatched   : {result['mismatched']}"
        )
        print(
            f"Exceptions   : {result['total_exceptions']}"
        )

    finally:
        db.close()


if __name__ == "__main__":
    main()