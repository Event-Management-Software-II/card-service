from flask import Flask

from .prisma_client import connect_db


def create_app():
    app = Flask(__name__)

    from .config import Config
    app.config.from_object(Config)

    connect_db()

    from .routes import mastercard_bp
    app.register_blueprint(mastercard_bp)

    return app
