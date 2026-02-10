from app.Extensions.db import db
from app.Domain.enums.FlightStatus import FlightStatus
from datetime import datetime

class Flight(db.Model):
    __tablename__ = 'flights'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    airline_id = db.Column(db.Integer, db.ForeignKey('airlines.id'), nullable=False)
    distance_km = db.Column(db.Float, nullable=False)
    duration_minutes = db.Column(db.Integer, nullable=False)
    departure_time = db.Column(db.DateTime, nullable=False)
    departure_airport = db.Column(db.String(100), nullable=False)
    arrival_airport = db.Column(db.String(100), nullable=False)
    created_by_user_id = db.Column(db.Integer, nullable=False)  # Manager ID
    ticket_price = db.Column(db.Float, nullable=False)
    
    # Status tracking
    status = db.Column(db.Enum(FlightStatus), nullable=False, default=FlightStatus.PENDING)
    rejection_reason = db.Column(db.Text, nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    airline = db.relationship('Airline', back_populates='flights')