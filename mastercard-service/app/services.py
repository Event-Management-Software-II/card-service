from decimal import Decimal
from datetime import datetime

from .models import Card, CardTransaction, CardTransactionStatus, card_transaction_to_dict
from .prisma_client import get_session


def clean_pan(pan: str) -> str:
    return str(pan).replace(" ", "").replace("-", "")


def validate_pan_format(pan: str) -> tuple[bool, str]:
    clean = clean_pan(pan)
    if not clean.isdigit():
        return False, "Card number must contain only digits"
    if len(clean) != 16:
        return False, "Card number must have 16 digits"
    if not clean.startswith("5"):
        return False, "Card does not belong to Mastercard"
    return True, ""


def validate_expiry(expiry: str) -> tuple[bool, str]:
    try:
        month, year = expiry.strip().split("/")
        month = int(month)
        year = int("20" + year)
        if not (1 <= month <= 12):
            return False, "Invalid expiry month"
        now = datetime.now()
        if year < now.year or (year == now.year and month < now.month):
            return False, "Card is expired"
        return True, ""
    except Exception:
        return False, "Invalid expiry format, use MM/YY"


def validate_customer(pan: str, cvv: str) -> dict:
    clean = clean_pan(pan)

    ok, reason = validate_pan_format(clean)
    if not ok:
        return {"ok": False, "error": reason}

    if not str(cvv).isdigit() or len(str(cvv)) not in (3, 4):
        return {"ok": False, "error": "CVV must have 3 or 4 digits"}

    with get_session() as session:
        card = session.query(Card).filter(Card.pan == clean).first()
        if not card:
            return {"ok": False, "error": "Card not registered in Mastercard service"}
        if not card.isActive:
            return {"ok": False, "error": "Card is not active"}
        if card.cvv != str(cvv):
            return {"ok": False, "error": "Invalid CVV"}

    return {
        "ok": True,
        "service": "mastercard",
        "card": f"**** **** **** {clean[-4:]}",
    }


def charge_card(
    pan: str,
    amount: float,
    reference: str | None = None,
    card_holder: str | None = None,
) -> dict:
    clean = clean_pan(pan)
    last_four = clean[-4:] if len(clean) >= 4 else "0000"
    amt = Decimal(str(amount))

    with get_session() as session:
        def reject(reason: str):
            tx = CardTransaction(
                lastFourDigits=last_four,
                amount=amt,
                status=CardTransactionStatus.rejected,
                rejectionReason=reason,
                reference=reference,
                cardHolder=card_holder,
            )
            session.add(tx)
            session.commit()
            session.refresh(tx)
            return card_transaction_to_dict(tx)

        ok, reason = validate_pan_format(clean)
        if not ok:
            return reject(reason)

        card = session.query(Card).filter(Card.pan == clean).first()
        if not card or not card.isActive:
            return reject("Card not registered or inactive")

        if card.balance < amt:
            return reject("Insufficient balance")

        card.balance = card.balance - amt
        session.add(card)

        tx = CardTransaction(
            lastFourDigits=last_four,
            amount=amt,
            status=CardTransactionStatus.approved,
            reference=reference,
            cardHolder=card_holder,
        )
        session.add(tx)
        session.commit()
        session.refresh(tx)
        return card_transaction_to_dict(tx)


def list_transactions() -> list[dict]:
    with get_session() as session:
        txs = session.query(CardTransaction).order_by(CardTransaction.createdAt.desc()).all()
        return [card_transaction_to_dict(t) for t in txs]
