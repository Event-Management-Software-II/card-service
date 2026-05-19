from flask import Flask
from flasgger import Swagger

from .middleware import log_request, log_response, handle_error
from .logger import logger

SWAGGER_CONFIG = {
    "title": "Mastercard Service API",
    "version": "1.0.0",
    "description": (
        "Servicio interno de validación y cobro de tarjetas Mastercard (prefijo 5). "
        "Gestiona tarjetas registradas en base de datos y registra cada transacción."
    ),
    "uiversion": 3,
    "specs_route": "/api-docs/",
}

SWAGGER_TEMPLATE = {
    "openapi": "3.0.0",
    "info": {
        "title": "Mastercard Service API",
        "version": "1.0.0",
        "description": SWAGGER_CONFIG["description"],
    },
    "servers": [{"url": "http://localhost:3003", "description": "Servidor local"}],
    "paths": {
        "/health": {
            "get": {
                "tags": ["Sistema"],
                "summary": "Health check",
                "responses": {
                    "200": {
                        "description": "Servicio activo",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "service": {"type": "string", "example": "mastercard"},
                                        "status": {"type": "string", "example": "active"},
                                    },
                                }
                            }
                        },
                    }
                },
            }
        },
        "/api/validate": {
            "post": {
                "tags": ["Tarjetas"],
                "summary": "Validar tarjeta Mastercard",
                "description": (
                    "Verifica que la tarjeta exista en el sistema, esté activa y que el CVV sea correcto. "
                    "El PAN debe ser de 16 dígitos y comenzar con 5."
                ),
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "required": ["pan", "cvv"],
                                "properties": {
                                    "pan": {"type": "string", "example": "5412345678901234", "description": "Número de tarjeta (16 dígitos, prefijo 5)"},
                                    "cvv": {"type": "string", "example": "123", "description": "Código de seguridad (3-4 dígitos)"},
                                },
                            }
                        }
                    },
                },
                "responses": {
                    "200": {
                        "description": "Tarjeta válida",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "ok": {"type": "boolean", "example": True},
                                        "service": {"type": "string", "example": "mastercard"},
                                        "card": {
                                            "type": "object",
                                            "properties": {
                                                "holder": {"type": "string"},
                                                "lastFour": {"type": "string"},
                                            },
                                        },
                                    },
                                }
                            }
                        },
                    },
                    "400": {"description": "Campos faltantes (pan o cvv)"},
                    "422": {
                        "description": "Tarjeta inválida (no encontrada, inactiva o CVV incorrecto)",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "ok": {"type": "boolean", "example": False},
                                        "error": {"type": "string"},
                                    },
                                }
                            }
                        },
                    },
                },
            }
        },
        "/api/charge": {
            "post": {
                "tags": ["Tarjetas"],
                "summary": "Cobrar a una tarjeta Mastercard",
                "description": (
                    "Debita el monto indicado del saldo de la tarjeta y registra la transacción. "
                    "Retorna 422 si la tarjeta no existe, está inactiva o no tiene saldo suficiente."
                ),
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "required": ["pan", "amount"],
                                "properties": {
                                    "pan": {"type": "string", "example": "5412345678901234"},
                                    "amount": {"type": "number", "example": 150000, "description": "Monto a cobrar (> 0)"},
                                    "reference": {"type": "string", "example": "ORD-2024-001"},
                                    "cardHolder": {"type": "string", "example": "Juan Pérez"},
                                },
                            }
                        }
                    },
                },
                "responses": {
                    "201": {
                        "description": "Cobro aprobado",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "status": {"type": "string", "example": "approved"},
                                        "id": {"type": "integer"},
                                        "amount": {"type": "number"},
                                        "reference": {"type": "string"},
                                        "cardHolder": {"type": "string"},
                                        "lastFourDigits": {"type": "string"},
                                        "createdAt": {"type": "string", "format": "date-time"},
                                    },
                                }
                            }
                        },
                    },
                    "400": {"description": "Campos faltantes o monto inválido"},
                    "422": {
                        "description": "Cobro rechazado (saldo insuficiente, tarjeta inactiva, etc.)",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "status": {"type": "string", "example": "rejected"},
                                        "rejectionReason": {"type": "string"},
                                    },
                                }
                            }
                        },
                    },
                },
            }
        },
        "/transactions": {
            "get": {
                "tags": ["Transacciones"],
                "summary": "Listar todas las transacciones",
                "responses": {
                    "200": {
                        "description": "Lista de transacciones",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "id": {"type": "integer"},
                                            "cardNumber": {"type": "string", "example": "**** **** **** 1234"},
                                            "amount": {"type": "number"},
                                            "status": {"type": "string", "enum": ["approved", "rejected"]},
                                            "rejectionReason": {"type": "string", "nullable": True},
                                            "reference": {"type": "string"},
                                            "cardHolder": {"type": "string"},
                                            "createdAt": {"type": "string", "format": "date-time"},
                                        },
                                    },
                                }
                            }
                        },
                    }
                },
            }
        },
    },
}


def create_app():
    app = Flask(__name__)

    from .config import Config
    app.config.from_object(Config)

    Swagger(app, config={"specs_route": "/api-docs/"}, template=SWAGGER_TEMPLATE)

    app.before_request(log_request)
    app.after_request(log_response)
    app.register_error_handler(Exception, handle_error)

    from .routes import mastercard_bp
    app.register_blueprint(mastercard_bp)

    logger.info("Mastercard service initialized")

    return app
