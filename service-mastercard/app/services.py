from decimal import Decimal

from .models import card_transaction_to_dict
from .prisma_client import db


def clean_card_number(card_number: str) -> str:
    return str(card_number).replace(" ", "").replace("-", "")


def validate_card_number(card_number: str) -> tuple[bool, str]:
    clean_number = clean_card_number(card_number)

    if not clean_number.isdigit():
        return False, "The card number must contain only digits"

    if len(clean_number) != 16:
        return False, "The card number must have 16 digits"

    if not clean_number.startswith("5"):
        return False, "The card does not belong to Mastercard"

    return True, ""


def validate_customer(pan: str, cvv: str) -> dict:
    is_valid, reason = validate_card_number(pan)
    is_cvv_valid = str(cvv).isdigit() and len(str(cvv)) in (3, 4)

    if not is_valid:
        return {"ok": False, "error": reason}

    if not is_cvv_valid:
        return {"ok": False, "error": "The CVV must have 3 or 4 digits"}

    return {
        "ok": True,
        "service": "mastercard",
        "card": f"**** **** **** {clean_card_number(pan)[-4:]}",
    }


def charge_card(
    card_number: str,
    amount: float,
    reference: str | None = None,
    card_holder: str | None = None,
) -> dict:
    clean_number = clean_card_number(card_number)
    last_four_digits = clean_number[-4:] if len(clean_number) >= 4 else "0000"
    is_valid, reason = validate_card_number(clean_number)
    status = "approved" if is_valid else "rejected"
    rejection_reason = None if is_valid else reason

    transaction = db.cardtransaction.create(
        data={
            "lastFourDigits": last_four_digits,
            "amount": Decimal(str(amount)),
            "status": status,
            "rejectionReason": rejection_reason,
            "reference": reference,
            "cardHolder": card_holder,
        }
    )

    return card_transaction_to_dict(transaction)


def list_transactions() -> list[dict]:
    transactions = db.cardtransaction.find_many(order={"createdAt": "desc"})
    return [card_transaction_to_dict(transaction) for transaction in transactions]
