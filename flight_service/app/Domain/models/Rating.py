from app.Extensions.db import db
from datetime import datetime

class Rating(db.Model):
    __tablename__ = 'ratings'

    id = db.Column(db.Integer, primary_key=True, autoicnrement=True)
    user_id = db.Column(db.Integer, nullable=False)
    flight_id = db.Column(db.Integer, db.ForeignKey('flights.id'),nullable=False)
    rating = db.Column(db.Integer, nullable=False) #Ocena 1-5
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    flight = db.relationship('Flight', backref='ratings', lazy=True)