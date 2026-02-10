from flask import Flask
from app.Extensions.db import db
from app.Extensions.cors import cors
from app.API.flights import flights_bp
from app.API.airlines import airlines_bp
from app.Config.config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    db.init_app(app)
    cors.init_app(app)
    
    app.register_blueprint(flights_bp)
    app.register_blueprint(airlines_bp)
    
    with app.app_context():
        db.create_all()
    
    return app