from flask import Flask
from app.extensions import db, jwt, cors

def create_app():
    app = Flask(__name__)

    db.init_app(app)
    jwt.init_app(app)
    cors.init_app(app)

    return app