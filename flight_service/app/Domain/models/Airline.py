from app.Extensions.db import db

class Airline(db.Model):
    __tablename__ = 'airlines'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    code = db.Column(db.String(10), unique=True, nullable=False)  # e.g., "AA", "BA"
    country = db.Column(db.String(50), nullable=False)
    
    # Relationship
    flights = db.relationship('Flight', back_populates='airline', lazy=True, cascade='all, delete-orphan')