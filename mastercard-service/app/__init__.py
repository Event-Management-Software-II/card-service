from flask import Flask

from .middleware import log_request, log_response, handle_error
from .logger import logger


def create_app():
    app = Flask(__name__)

    from .config import Config
    app.config.from_object(Config)

    app.before_request(log_request)
    app.after_request(log_response)
    app.register_error_handler(Exception, handle_error)

    from .routes import mastercard_bp
    app.register_blueprint(mastercard_bp)

    logger.info("Mastercard service initialized")

    return app
