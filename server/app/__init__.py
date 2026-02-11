import os
from app.WebSockets.events import register_socketio_events
from flask import Flask, send_from_directory
from app.Extensions import db, jwt, cors, socketio
from app.API.auth import auth_bp
from app.API.users import users_bp
from app.API.flights import flights_bp
from app.API.airlines import airlines_bp
from app.API.purchases import purchase_bp
from app.API.ratings import rating_bp
import app.Config.config as config

def create_app():
    app = Flask(__name__)
    app.config.from_object(config.Config)

    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    db.init_app(app)
    jwt.init_app(app)
    cors.init_app(
        app,
        resources={r"/api/*": {"origins": app.config["CORS_ORIGINS"]}},
        supports_credentials=True,
        allow_headers=["Authorization", "Content-Type"],
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    )
    socketio.init_app(
        app, 
        cors_allowed_origins="*",
        async_mode='eventlet',
        logger=True,
        engineio_logger=True
    )
    register_socketio_events(socketio)

    app.register_blueprint(auth_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(flights_bp)
    app.register_blueprint(airlines_bp)
    app.register_blueprint(purchase_bp)
    app.register_blueprint(rating_bp)

    @app.route("/uploads/<path:filename>")
    def uploaded_file(filename):
        return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

    with app.app_context():
        db.create_all()

    return app