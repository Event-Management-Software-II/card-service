from flask import Blueprint, jsonify, request

from .services import charge_card, list_transactions, validate_customer

mastercard_bp = Blueprint("mastercard", __name__)


@mastercard_bp.route("/health", methods=["GET"])
def health():
    return jsonify({"service": "mastercard", "status": "active"}), 200


@mastercard_bp.route("/api/validate", methods=["POST"])
def validate():
    payload = request.get_json() or {}
    pan = payload.get("pan") or payload.get("cardNumber")
    cvv = payload.get("cvv")

    if not pan or not cvv:
        return jsonify({"ok": False, "error": "pan and cvv are required"}), 400

    result = validate_customer(pan, cvv)
    if not result["ok"]:
        return jsonify(result), 422

    return jsonify(result), 200


@mastercard_bp.route("/api/charge", methods=["POST"])
def charge():
    return process_charge(request.get_json() or {})


def process_charge(payload):
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

    result = charge_card(
        card_number=str(pan),
        amount=amount,
        reference=payload.get("reference"),
        card_holder=payload.get("cardHolder"),
    )

    if result["status"] == "rejected":
        return jsonify(result), 422

    return jsonify(result), 201


@mastercard_bp.route("/process-payment", methods=["POST"])
def process_payment():
    return process_charge(request.get_json() or {})


@mastercard_bp.route("/transactions", methods=["GET"])
def transactions():
    return jsonify(list_transactions()), 200
