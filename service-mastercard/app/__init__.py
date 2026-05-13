from flask import Flask
from sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    app=Flask(__serviceMastercard__)
    
    from .config import Config
    app.config.from_object(Config)
    
    db.init_app(app)
    
    from .routes import mastercard_bp
    app.register_blueprint(mastercard_bp)
    with app.app_context():
        db.create_all()
        
    return app