from flask import Blueprint, jsonify, request

from app.API.ratings.RatingService import RatingService

rating_bp = Blueprint("rating_bp", __name__, url_prefix="/api/v1")


@rating_bp.route("/rating", methods=["POST"])
def create_rating():
    data = request.get_json() or {}

    try:
        result = RatingService.create_rating(data)
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@rating_bp.route("/ratings", methods=["GET"])
def get_all_ratings():
    try:
        ratings = RatingService.get_all_ratings()
        return jsonify(ratings), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500
