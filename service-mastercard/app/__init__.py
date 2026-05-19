from flask import Flask
from flask_sqlalchemy import SQLAlchemy  # ← fix 1: flask_sqlalchemy, no sqlalchemy

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)  # ← fix 2: __name__, no __serviceMastercard__
    
    from .config import Config
    app.config.from_object(Config)
    
    db.init_app(app)
    
    from .routes import mastercard_bp
    app.register_blueprint(mastercard_bp)
    
    with app.app_context():
        db.create_all()
        
    return app