from . import db
from .models import TransaccionMastercard

def validar_numero_tarjeta(numero_tarjeta: str) -> tuple[bool, str]:
    numero_limpio = numero_tarjeta.replace(" ", "").replace("-", "")

    if not numero_limpio.isdigit():
        return False, "El número de tarjeta solo debe contener dígitos"

    if len(numero_limpio) != 16:
        return False, "El número de tarjeta debe tener 16 dígitos"

    return True, ""

def procesar_pago(numero_tarjeta: str, monto: float) -> dict:
    numero_limpio  = numero_tarjeta.replace(" ", "").replace("-", "")
    ultimos_cuatro = numero_limpio[-4:] if len(numero_limpio) >= 4 else "0000"

    # --- Validar formato básico ---
    es_valida, motivo = validar_numero_tarjeta(numero_limpio)

    estado         = "aprobado" if es_valida else "rechazado"
    motivo_rechazo = None if es_valida else motivo

    # --- Registrar en BD ---
    transaccion = TransaccionMastercard(
        numero_tarjeta = ultimos_cuatro,
        monto          = monto,
        estado         = estado,
        motivo_rechazo = motivo_rechazo,
    )
    db.session.add(transaccion)
    db.session.commit()

    return {
        "transaccion_id": transaccion.id,
        "estado":         estado,
        "motivo_rechazo": motivo_rechazo,
        "monto":          monto,
        "tarjeta":        f"**** **** **** {ultimos_cuatro}",
    }