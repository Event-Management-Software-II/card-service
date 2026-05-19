from decimal import Decimal
from datetime import datetime

from .logger import logger, transaction_logger
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
    masked = f"**** **** **** {clean[-4:]}"

    ok, reason = validate_pan_format(clean)
    if not ok:
        logger.warning(f"Validation rejected [{masked}]: {reason}")
        return {"ok": False, "error": reason}

    if not str(cvv).isdigit() or len(str(cvv)) not in (3, 4):
        logger.warning(f"Validation rejected [{masked}]: invalid CVV format")
        return {"ok": False, "error": "CVV must have 3 or 4 digits"}

    with get_session() as session:
        card = session.query(Card).filter(Card.pan == clean).first()
        if not card:
            logger.warning(f"Validation rejected [{masked}]: card not registered")
            return {"ok": False, "error": "Card not registered in Mastercard service"}
        if not card.isActive:
            logger.warning(f"Validation rejected [{masked}]: card inactive")
            return {"ok": False, "error": "Card is not active"}
        if card.cvv != str(cvv):
            logger.warning(f"Validation rejected [{masked}]: wrong CVV")
            return {"ok": False, "error": "Invalid CVV"}

    logger.info(f"Validation approved [{masked}]")
    return {
        "ok": True,
        "service": "mastercard",
        "card": masked,
    }


def charge_card(
    pan: str,
    amount: float,
    reference: str | None = None,
    card_holder: str | None = None,
) -> dict:
    clean = clean_pan(pan)
    last_four = clean[-4:] if len(clean) >= 4 else "0000"
    masked = f"**** **** **** {last_four}"
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
            transaction_logger.warning(
                f"CHARGE REJECTED | [{masked}] | Amount: {amt} | Reason: {reason} | Ref: {reference}"
            )
            return card_transaction_to_dict(tx)

        ok, reason = validate_pan_format(clean)
        if not ok:
            logger.warning(f"Charge rejected [{masked}]: {reason}")
            return reject(reason)

        card = session.query(Card).filter(Card.pan == clean).first()
        if not card or not card.isActive:
            logger.warning(f"Charge rejected [{masked}]: card not registered or inactive")
            return reject("Card not registered or inactive")

        if card.balance < amt:
            logger.warning(
                f"Charge rejected [{masked}]: insufficient balance "
                f"(balance={card.balance}, requested={amt})"
            )
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

        transaction_logger.info(
            f"CHARGE APPROVED | [{masked}] | Amount: {amt} | "
            f"Ref: {reference} | Holder: {card_holder} | TxID: {tx.id}"
        )
        logger.info(f"Charge approved [{masked}] amount={amt} ref={reference}")
        return card_transaction_to_dict(tx)


def list_transactions() -> list[dict]:
    with get_session() as session:
        txs = session.query(CardTransaction).order_by(CardTransaction.createdAt.desc()).all()
        logger.debug(f"Listed {len(txs)} transactions")
        return [card_transaction_to_dict(t) for t in txs]