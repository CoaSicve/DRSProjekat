from flask import Blueprint, jsonify, request
from app.API.ratings.RatingService import RatingService
from app.Domain.models.Rating import Rating

rating_bp = Blueprint("rating_bp", __name__)

@rating_bp.route("/rating", methods=["POST"])
def create_rating():
    data = request.get_json()
    user_id = data.get("user_id")
    flight_id = data.get("flight_id")
    rating_value = data.get("rating")

    try:
        rating = RatingService.add_rating(user_id, flight_id, rating_value)
        return jsonify({
            "message": "Ocena je uspesno dodata.",
            "rating_id": rating.id
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    
@rating_bp.route("/ratings", methods=["GET"])
def get_all_ratings():
    ratings = Rating.query.all()
    return jsonify([
        {
            "id": r.id,
            "user_id": r.user_id,
            "flight_id": r.flight_id,
            "rating": r.rating,
            "created_at": r.created_at.isoformat()
        } for r in ratings
    ])