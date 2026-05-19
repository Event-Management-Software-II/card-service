import enum
from decimal import Decimal
from datetime import datetime

from sqlalchemy import (
    Boolean, Column, DateTime, Enum, Integer, Numeric, String, text
)

from .prisma_client import Base


class CardTransactionStatus(str, enum.Enum):
    approved = "approved"
    rejected = "rejected"


class Card(Base):
    __tablename__ = "cards"

    id = Column(Integer, primary_key=True, autoincrement=True)
    pan = Column(String(16), unique=True, nullable=False)
    cvv = Column(String(4), nullable=False)
    expiry = Column(String(5), nullable=False)
    holder = Column(String(100), nullable=False)
    balance = Column(Numeric(12, 2), nullable=False, default=0)
    isActive = Column("isActive", Boolean, nullable=False, default=True)


class CardTransaction(Base):
    __tablename__ = "card_transactions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    lastFourDigits = Column("lastFourDigits", String(4), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    status = Column(
        Enum(CardTransactionStatus, name="CardTransactionStatus", create_constraint=False),
        nullable=False,
    )
    rejectionReason = Column("rejectionReason", String(255), nullable=True)
    reference = Column(String(100), nullable=True)
    cardHolder = Column("cardHolder", String(100), nullable=True)
    createdAt = Column(
        "createdAt", DateTime, nullable=False, server_default=text("NOW()")
    )


def card_transaction_to_dict(t: CardTransaction) -> dict:
    return {
        "id": t.id,
        "cardNumber": f"**** **** **** {t.lastFourDigits}",
        "amount": float(t.amount),
        "status": t.status.value if isinstance(t.status, CardTransactionStatus) else t.status,
        "rejectionReason": t.rejectionReason,
        "reference": t.reference,
        "cardHolder": t.cardHolder,
        "createdAt": t.createdAt.isoformat() if t.createdAt else None,
    }
