from flask import Blueprint, jsonify, request, current_app
from pydantic import ValidationError
from app.API.flights.FlightService import FlightService
from app.Domain.DTOs.FlightDTO import CreateFlightDTO
from app.Middleware.auth import jwt_required_custom, get_current_user, admin_required, manager_or_admin_required

flights_bp = Blueprint("flights", __name__, url_prefix="/api/v1/flights")

@flights_bp.route("", methods=["GET"])
def get_all_flights():
    """Javni endpoint - ne zahteva autentifikaciju"""
    try:
        flights = FlightService.get_all_flights()
        return jsonify([f.model_dump() for f in flights]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@flights_bp.route("/<int:flight_id>", methods=["GET"])
def get_flight(flight_id: int):
    """Javni endpoint - ne zahteva autentifikaciju"""
    try:
        flight = FlightService.get_flight_by_id(flight_id)
        return jsonify(flight.model_dump()), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404

@flights_bp.route("", methods=["POST"])
@jwt_required_custom 
def create_flight():
    """Kreiranje leta - SAMO ZA MANAGER"""
    try:
        data = request.get_json()
        dto = CreateFlightDTO(**data)
        user = get_current_user()
        if user["role"] != "MANAGER":
            return jsonify({"error": "Only MANAGER can create flights"}), 403
        print("test4")
        flight = FlightService.create_flight(dto, user["user_id"], user["email"])
        return jsonify(flight.model_dump()), 201
    except ValidationError as e:
        return jsonify({"error": e.errors()}), 400
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@flights_bp.route("/<int:flight_id>", methods=["PUT"])
@manager_or_admin_required
def update_flight(flight_id: int):
    """Izmena leta - MANAGER ili ADMIN"""
    try:
        data = request.get_json()
        dto = CreateFlightDTO(**data)
        user = get_current_user()
        flight = FlightService.update_flight(flight_id, dto, user)
        return jsonify(flight.model_dump()), 200
    except ValidationError as e:
        return jsonify({"error": e.errors()}), 400
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@flights_bp.route("/<int:flight_id>/approve", methods=["PUT"])
@admin_required  # Samo ADMIN
def approve_flight(flight_id: int):
    """Odobravanje leta - SAMO ZA ADMIN"""
    try:
        user = get_current_user()
        flight = FlightService.approve_flight(flight_id, user["email"])
        return jsonify(flight.model_dump()), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404

@flights_bp.route("/<int:flight_id>/reject", methods=["PUT"])
@admin_required  # Samo ADMIN
def reject_flight(flight_id: int):
    """Odbijanje leta - SAMO ZA ADMIN"""
    try:
        data = request.get_json()
        reason = data.get("reason", "No reason provided")
        user = get_current_user()
        flight = FlightService.reject_flight(flight_id, reason, user["email"])
        return jsonify(flight.model_dump()), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404

@flights_bp.route("/<int:flight_id>/cancel", methods=["PUT"])
@admin_required
def cancel_flight(flight_id: int):
    try:

        user = get_current_user()

        auth_header = request.headers.get("Authorization", "")
        token = auth_header.replace("Bearer ", "").strip()

        server_base_url = current_app.config.get("SERVER_URL")

        flight = FlightService.cancel_flight(
            flight_id,
            user["email"],
            token,
            server_base_url
        )

        return jsonify(flight.model_dump()), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 404

@flights_bp.route("/<int:flight_id>", methods=["DELETE"])
@admin_required  #  Samo ADMIN
def delete_flight(flight_id: int):
    """Brisanje leta - SAMO ZA ADMIN"""
    try:
        print(f"Delete request for flight_id: {flight_id}")
        FlightService.delete_flight(flight_id)
        return jsonify({"message": "Flight deleted successfully"}), 200
    except ValueError as e:
        print(f"Delete error: {str(e)}")
        return jsonify({"error": str(e)}), 404