import os
from dotenv import load_dotenv

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
load_dotenv(os.path.join(BASE_DIR, ".env"))

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")

    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL", 
        "mysql+pymysql://root:1234@db:3306/drs_users_db"
    )
    
    SQLALCHEMY_BINDS = {
        'flights_db': os.getenv(
            "FLIGHTS_DATABASE_URL",
            "mysql+pymysql://root:1234@db:3306/drs_flights_db"
        )
    }
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-jwt-secret-key-change-in-production")
    JWT_ACCESS_TOKEN_EXPIRES = 3600
    CORS_ORIGINS = [origin.strip() for origin in os.getenv(
        "CORS_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173"
    ).split(",") if origin.strip()]