from flask import Flask
from app.Extensions.db import db
from app.Extensions.socketio import socketio
from app.Extensions.mail import mail
from app.Extensions.jwt import jwt
from app.WebSockets.events import register_socketio_events
from app.Services.FlightStatusWatcher import FlightStatusWatcher
from app.Extensions.cors import cors
from app.API.flights import flights_bp
from app.API.airlines import airlines_bp
from app.Config.config import Config
from app.API.test_mail import test_mail_bp
from app.API.purchases import purchase_bp
from app.API.ratings import rating_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    db.init_app(app)
    mail.init_app(app)
    jwt.init_app(app)
    cors.init_app(app)
    socketio.init_app(
        app, 
        cors_allowed_origins="*",
        async_mode='eventlet',
        logger=True,
        engineio_logger=True
    )
    register_socketio_events(socketio)
    
    app.register_blueprint(flights_bp)
    app.register_blueprint(airlines_bp)

    app.register_blueprint(purchase_bp)
    app.register_blueprint(rating_bp)
    
    app.register_blueprint(test_mail_bp)
    
    with app.app_context():
        db.create_all()

    FlightStatusWatcher.start(interval_seconds=5)
    
    return app