from datetime import datetime
from . import db


class TransaccionMastercard(db.Model):
    __tablename__ = "transacciones_mastercard"
    id             = db.Column(db.Integer, primary_key=True)
    numero_tarjeta = db.Column(db.String(4), nullable=False)
    monto          = db.Column(db.Numeric(10, 2), nullable=False)
    estado         = db.Column(db.String(20), nullable=False)
    motivo_rechazo = db.Column(db.String(255), nullable=True)
    fecha          = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id":             self.id,
            "numero_tarjeta": f"**** **** **** {self.numero_tarjeta}",
            "monto":          float(self.monto),
            "estado":         self.estado,
            "motivo_rechazo": self.motivo_rechazo,
            "fecha":          self.fecha.isoformat(),
        }
