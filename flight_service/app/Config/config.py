import os

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "flight-service-secret")
    
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL", 
        "mysql+pymysql://root:1234@db:3306/drs_flights_db"
    )
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Flask-Mail
    MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = int(os.getenv("MAIL_PORT", "587"))
    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "true").lower() == "true"
    MAIL_USE_SSL = os.getenv("MAIL_USE_SSL", "false").lower() == "true"
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER", MAIL_USERNAME)
    MAIL_ENABLED = os.getenv("MAIL_ENABLED", "true").lower() == "true"
    MAIL_TEST_TO = os.getenv("MAIL_TEST_TO")
    MAIL_FROM_NAME = os.getenv("MAIL_FROM_NAME", "DRS Flight Service")

    # SocketIO (opciono)
    SOCKETIO_CORS_ALLOWED_ORIGINS = os.getenv("SOCKETIO_CORS_ALLOWED_ORIGINS", "*")