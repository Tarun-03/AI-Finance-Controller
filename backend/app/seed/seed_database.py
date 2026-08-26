from sqlalchemy import delete

from app.db.session import SessionLocal
from app.models.invoice import Invoice
from app.models.payment import Payment
from app.models.settlement import Settlement
from app.models.transaction import Transaction
from app.seed.generator import generate_dataset
from app.seed.scenarios import SCENARIOS, apply_all_scenarios


def seed_database(count: int = 100) -> None:
    db = SessionLocal()

    try:
        print("Clearing existing finance data...")

        db.execute(delete(Payment))
        db.execute(delete(Settlement))
        db.execute(delete(Invoice))
        db.execute(delete(Transaction))

        print(f"Generating {count} transactions...")

        dataset = generate_dataset(count)
        dataset = apply_all_scenarios(dataset)

        print("\nScenario distribution:")

        for scenario, transaction_ids in SCENARIOS.items():
            print(
                f"  {scenario}: {len(transaction_ids)}"
            )

        for record in dataset:

            transaction = Transaction(
                **record["transaction"]
            )

            db.add(transaction)
            db.flush()

            if record["payment"] is not None:
                db.add(
                    Payment(**record["payment"])
                )

            if record["settlement"] is not None:
                db.add(
                    Settlement(**record["settlement"])
                )

            if record["invoice"] is not None:
                db.add(
                    Invoice(**record["invoice"])
                )

        db.commit()

        print(
            f"Successfully seeded {count} transactions."
        )

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    seed_database()