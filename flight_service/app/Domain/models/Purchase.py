from app.Extensions.db import db
from datetime import datetime
from app.Domain.enums.PurchaseStatus import PurchaseStatus

class Purchase(db.Model):
    __tablename__ = 'purchases'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, nullable=False)
    flight_id = db.Column(db.Integer, db.ForeignKey('flights.id'), nullable=False)
    purchase_time = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.Enum(PurchaseStatus), nullable=False, default='IN_PROGRESS')
    ticket_price = db.Column(db.Float, nullable=False)

    flight = db.relationship('Flight', backref='purchases', lazy=True)