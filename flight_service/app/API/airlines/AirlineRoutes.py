from flask import Blueprint, jsonify, request
from pydantic import ValidationError

from app.API.airlines.AirlineService import AirlineService
from app.Domain.DTOs.AirlineDTO import CreateAirlineDTO

airlines_bp = Blueprint("airlines", __name__, url_prefix="/api/v1/airlines")


@airlines_bp.route("", methods=["GET"])
def get_all_airlines():
    try:
        airlines = AirlineService.get_all_airlines()
        return jsonify([a.model_dump() for a in airlines]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@airlines_bp.route("/<int:airline_id>", methods=["GET"])
def get_airline(airline_id: int):
    try:
        airline = AirlineService.get_airline_by_id(airline_id)
        return jsonify(airline.model_dump()), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404


@airlines_bp.route("", methods=["POST"])
def create_airline():
    try:
        dto = CreateAirlineDTO(**request.get_json())
        airline = AirlineService.create_airline(dto)
        return jsonify(airline.model_dump()), 201
    except ValidationError as e:
        return jsonify({"error": e.errors()}), 400
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@airlines_bp.route("/<int:airline_id>", methods=["DELETE"])
def delete_airline(airline_id: int):
    try:
        AirlineService.delete_airline(airline_id)
        return jsonify({"message": "Airline deleted successfully"}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404