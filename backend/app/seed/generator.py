import random
import uuid
from datetime import datetime, timedelta, timezone
from decimal import Decimal


RANDOM_SEED = 42

MERCHANTS = [
    "MERCHANT_001",
    "MERCHANT_002",
    "MERCHANT_003",
    "MERCHANT_004",
    "MERCHANT_005",
]

PAYMENT_METHODS = [
    "UPI",
    "CARD",
    "NET_BANKING",
    "WALLET",
]

GATEWAYS = [
    "RAZORPAY",
    "STRIPE",
    "PAYU",
]


def random_amount(rng: random.Random) -> Decimal:
    return Decimal(rng.randint(100, 100000)).quantize(
        Decimal("0.01")
    )


def random_timestamp(rng: random.Random) -> datetime:
    now = datetime.now(timezone.utc)

    return now - timedelta(
        days=rng.randint(0, 30),
        minutes=rng.randint(0, 1439),
    )


def generate_transaction(
    rng: random.Random,
    index: int,
) -> dict:

    return {
        "id": uuid.uuid4(),
        "transaction_id": f"TXN_{index:06d}",
        "merchant_id": rng.choice(MERCHANTS),
        "customer_id": f"CUST_{rng.randint(1, 500):05d}",
        "amount": random_amount(rng),
        "currency": "INR",
        "transaction_type": "PAYMENT",
        "status": "SUCCESS",
        "transaction_date": random_timestamp(rng),
    }


def generate_payment(
    rng: random.Random,
    transaction: dict,
    index: int,
) -> dict:

    return {
        "id": uuid.uuid4(),
        "payment_id": f"PAY_{index:06d}",
        "transaction_id": transaction["id"],
        "amount": transaction["amount"],
        "payment_method": rng.choice(PAYMENT_METHODS),
        "gateway": rng.choice(GATEWAYS),
        "status": "SUCCESS",
        "payment_timestamp": transaction["transaction_date"],
    }


def generate_settlement(
    rng: random.Random,
    transaction: dict,
    index: int,
) -> dict:

    gross = transaction["amount"]

    fee = (
        gross * Decimal("0.02")
    ).quantize(Decimal("0.01"))

    tax = (
        fee * Decimal("0.18")
    ).quantize(Decimal("0.01"))

    net = gross - fee - tax

    return {
        "id": uuid.uuid4(),
        "settlement_id": f"SET_{index:06d}",
        "transaction_id": transaction["id"],
        "gross_amount": gross,
        "fee_amount": fee,
        "tax_amount": tax,
        "net_amount": net,
        "status": "SETTLED",
        "settlement_date": transaction["transaction_date"],
    }


def generate_invoice(
    rng: random.Random,
    transaction: dict,
    index: int,
) -> dict:

    tax = (
        transaction["amount"] * Decimal("0.18")
    ).quantize(Decimal("0.01"))

    invoice_amount = transaction["amount"] + tax

    invoice_date = transaction["transaction_date"]

    due_date = invoice_date + timedelta(days=30)

    return {
        "id": uuid.uuid4(),
        "invoice_id": f"INV_{index:06d}",
        "transaction_id": transaction["id"],
        "invoice_amount": invoice_amount,
        "tax_amount": tax,
        "status": "PAID",
        "invoice_date": invoice_date,
        "due_date": due_date,
    }


def generate_dataset(count: int = 100) -> list[dict]:

    rng = random.Random(RANDOM_SEED)

    dataset = []

    for index in range(1, count + 1):

        transaction = generate_transaction(
            rng,
            index,
        )

        payment = generate_payment(
            rng,
            transaction,
            index,
        )

        settlement = generate_settlement(
            rng,
            transaction,
            index,
        )

        invoice = generate_invoice(
            rng,
            transaction,
            index,
        )

        dataset.append(
            {
                "transaction": transaction,
                "payment": payment,
                "settlement": settlement,
                "invoice": invoice,
            }
        )

    return dataset