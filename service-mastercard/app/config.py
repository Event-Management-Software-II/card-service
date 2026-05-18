import os 
from dotenv import load_dotenv

load_dotenv()

class Config:
    DB_USER =os.getenv("DB_USEr", "mc_user")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "mc_password")
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5442")
    DB_NAME = os.getenv("DB_NAME", "mastercard_db")
    SQLALCHEMY_DATABASE_URI = (f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = os.getenv("FLASK_DEBUG", "False").lower() == "true"