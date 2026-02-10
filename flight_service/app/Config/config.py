import os

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "flight-service-secret")
    
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL", 
        "mysql+pymysql://root:1234@db:3306/drs_flights_db"
    )
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False