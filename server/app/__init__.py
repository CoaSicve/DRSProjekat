from flask import Flask
from app.Extensions import db, jwt, cors
from app.API.auth import auth_bp
from app.API.users import users_bp
from app.API.flights import flights_bp
from app.API.airlines import airlines_bp
import app.Config.config as config

def create_app():
    app = Flask(__name__)
    app.config.from_object(config.Config)

    db.init_app(app)
    jwt.init_app(app)
    cors.init_app(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(flights_bp)
    app.register_blueprint(airlines_bp)

    with app.app_context():
        db.create_all()

    return app