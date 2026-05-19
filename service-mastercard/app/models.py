def card_transaction_to_dict(transaction):
    return {
        "id": transaction.id,
        "cardNumber": f"**** **** **** {transaction.lastFourDigits}",
        "amount": float(transaction.amount),
        "status": transaction.status,
        "rejectionReason": transaction.rejectionReason,
        "reference": transaction.reference,
        "cardHolder": transaction.cardHolder,
        "createdAt": transaction.createdAt.isoformat(),
    }
