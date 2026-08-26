from decimal import Decimal


SCENARIOS = {
    "MATCHED": list(range(1, 71)),
    "AMOUNT_MISMATCH": list(range(71, 76)),
    "FEE_MISMATCH": list(range(76, 81)),
    "STATUS_MISMATCH": list(range(81, 86)),
    "MISSING_PAYMENT": list(range(86, 91)),
    "MISSING_SETTLEMENT": list(range(91, 96)),
    "MISSING_INVOICE": list(range(96, 101)),
}


def apply_amount_mismatch(dataset: list[dict]) -> None:
    for record in dataset:
        transaction = record["transaction"]
        index = int(transaction["transaction_id"].split("_")[1])

        if index in SCENARIOS["AMOUNT_MISMATCH"]:
            record["payment"]["amount"] += Decimal("500.00")


def apply_fee_mismatch(dataset: list[dict]) -> None:
    for record in dataset:
        transaction = record["transaction"]
        index = int(transaction["transaction_id"].split("_")[1])

        if index in SCENARIOS["FEE_MISMATCH"]:
            record["settlement"]["fee_amount"] += Decimal("100.00")

            record["settlement"]["net_amount"] = (
                record["settlement"]["gross_amount"]
                - record["settlement"]["fee_amount"]
                - record["settlement"]["tax_amount"]
            )


def apply_status_mismatch(dataset: list[dict]) -> None:
    for record in dataset:
        transaction = record["transaction"]
        index = int(transaction["transaction_id"].split("_")[1])

        if index in SCENARIOS["STATUS_MISMATCH"]:
            record["payment"]["status"] = "FAILED"


def apply_missing_payment(dataset: list[dict]) -> None:
    for record in dataset:
        transaction = record["transaction"]
        index = int(transaction["transaction_id"].split("_")[1])

        if index in SCENARIOS["MISSING_PAYMENT"]:
            record["payment"] = None


def apply_missing_settlement(dataset: list[dict]) -> None:
    for record in dataset:
        transaction = record["transaction"]
        index = int(transaction["transaction_id"].split("_")[1])

        if index in SCENARIOS["MISSING_SETTLEMENT"]:
            record["settlement"] = None


def apply_missing_invoice(dataset: list[dict]) -> None:
    for record in dataset:
        transaction = record["transaction"]
        index = int(transaction["transaction_id"].split("_")[1])

        if index in SCENARIOS["MISSING_INVOICE"]:
            record["invoice"] = None


def apply_all_scenarios(dataset: list[dict]) -> list[dict]:
    apply_amount_mismatch(dataset)
    apply_fee_mismatch(dataset)
    apply_status_mismatch(dataset)
    apply_missing_payment(dataset)
    apply_missing_settlement(dataset)
    apply_missing_invoice(dataset)

    return dataset