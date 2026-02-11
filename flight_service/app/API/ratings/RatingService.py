from app.Extensions.db import db
from app.Domain.models.Rating import Rating
from app.Domain.models.Flight import Flight
from datetime import datetime

class RatingService:
    @staticmethod
    def add_rating(user_id: int, flight_id: int, rating_value: int):
        flight = Flight.query.get(flight_id)
        if not flight:
            raise ValueError("Let ne postoji.")
        if flight.status.name != "COMPLETED":
            raise ValueError("Let jos nije zavrsen.")
        
        if rating_value < 1 or rating_value > 5:
            raise ValueError("Ocena mora biti u opsegu od 1 do 5.")
        
        existing_rating = Rating.query.filter_by(user_id=user_id, flight_id=flight_id).first()
        if existing_rating:
            raise ValueError("Korisnik je vec ocenio ovaj let.")
        
        new_rating = Rating(user_id=user_id, flight_id=flight_id, rating=rating_value)
        db.session.add(new_rating)
        db.session.commit()
        return new_rating