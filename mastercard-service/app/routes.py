from flask import Blueprint, jsonify, request, g

from .services import charge_card, list_transactions, validate_customer
from .logger import logger, transaction_logger

mastercard_bp = Blueprint("mastercard", __name__)


@mastercard_bp.route("/health", methods=["GET"])
def health():
    return jsonify({"service": "mastercard", "status": "active"}), 200


@mastercard_bp.route("/api/validate", methods=["POST"])
def validate():
    request_id = getattr(g, "request_id", "unknown")
    payload = request.get_json() or {}
    pan = payload.get("pan") or payload.get("cardNumber")
    cvv = payload.get("cvv")

    if not pan or not cvv:
        logger.warning(f"[{request_id}] Validation failed: missing fields")
        return jsonify({"ok": False, "error": "pan and cvv are required"}), 400

    logger.debug(f"[{request_id}] Validating card **** {pan[-4:]}")
    result = validate_customer(pan, cvv)

    if not result["ok"]:
        logger.warning(f"[{request_id}] Validation failed: {result.get('error')}")
        return jsonify(result), 422

    logger.info(f"[{request_id}] Card validated successfully")
    return jsonify(result), 200


@mastercard_bp.route("/api/charge", methods=["POST"])
def charge():
    request_id = getattr(g, "request_id", "unknown")
    payload = request.get_json() or {}
    pan = payload.get("pan") or payload.get("cardNumber")
    amount = payload.get("amount")

    if not pan:
        return jsonify({"error": "pan is required"}), 400
    if amount is None:
        return jsonify({"error": "amount is required"}), 400

    try:
        amount = float(amount)
    except (ValueError, TypeError):
        return jsonify({"error": "amount must be a valid number"}), 400

    if amount <= 0:
        return jsonify({"error": "amount must be greater than 0"}), 400

    logger.info(f"[{request_id}] Charging {amount} to card **** {pan[-4:]}")

    result = charge_card(
        pan=str(pan),
        amount=amount,
        reference=payload.get("reference"),
        card_holder=payload.get("cardHolder"),
    )

    transaction_logger.info(
        f"[{request_id}] CHARGE | Amount: {amount} | Status: {result['status']} | "
        f"Reference: {payload.get('reference')}"
    )

    if result["status"] == "rejected":
        logger.warning(f"[{request_id}] Charge rejected: {result.get('rejectionReason')}")
        return jsonify(result), 422

    logger.info(f"[{request_id}] Charge approved")
    return jsonify(result), 201


@mastercard_bp.route("/transactions", methods=["GET"])
def transactions():
    return jsonify(list_transactions()), 200
