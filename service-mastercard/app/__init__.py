from flask import Flask

from .prisma_client import connect_db
from .middleware import log_request, log_response, handle_error
from .logger import logger


def create_app():
    app = Flask(__name__)

    from .config import Config
    app.config.from_object(Config)

    # Registrar middlewares de logging
    app.before_request(log_request)
    app.after_request(log_response)
    app.register_error_handler(Exception, handle_error)

    connect_db()

    from .routes import mastercard_bp
    app.register_blueprint(mastercard_bp)

    logger.info("Card Service (Mastercard) initialized")

    return app
