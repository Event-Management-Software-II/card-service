from flask import Blueprint, request, jsonify
from .services import procesar_pago
from .models import TransaccionMastercard

mastercard_bp = Blueprint("mastercard", __name__)

@mastercard_bp.route("/health", methods=["GET"])
def health():
    return jsonify({"servicio": "mastercard", "estado": "activo"}), 200
    

@mastercard_bp.route("/procesar-pago", methods=["POST"])
def procesar():
    datos = request.get_json()

    if not datos:
        return jsonify({"error": "El cuerpo de la solicitud no puede estar vacío"}), 400

    if "numero_tarjeta" not in datos:
        return jsonify({"error": "El campo 'numero_tarjeta' es requerido"}), 400

    if "monto" not in datos:
        return jsonify({"error": "El campo 'monto' es requerido"}), 400

    try:
        monto = float(datos["monto"])
    except (ValueError, TypeError):
        return jsonify({"error": "El campo 'monto' debe ser un número válido"}), 400

    if monto <= 0:
        return jsonify({"error": "El monto debe ser mayor a 0"}), 400

    try:
        resultado = procesar_pago(
            numero_tarjeta=str(datos["numero_tarjeta"]),
            monto=monto,
        )
    except Exception as e:
        return jsonify({"error": "Error interno al procesar el pago", "detalle": str(e)}), 500

    if resultado["estado"] == "rechazado":
        return jsonify(resultado), 422

    return jsonify(resultado), 201

@mastercard_bp.route("/transacciones", methods=["GET"])
def listar_transacciones():
    transacciones = TransaccionMastercard.query.order_by(TransaccionMastercard.fecha.desc()).all()
    return jsonify([t.to_dict() for t in transacciones]), 200
