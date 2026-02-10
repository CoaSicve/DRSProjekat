from flask import Blueprint, jsonify, request
from pydantic import ValidationError
from app.API.flights.FlightService import FlightService
from app.Domain.DTOs.FlightDTO import CreateFlightDTO

flights_bp = Blueprint("flights", __name__, url_prefix="/api/v1/flights")

@flights_bp.route("", methods=["GET"])
def get_all_flights():
    try:
        flights = FlightService.get_all_flights()
        return jsonify([f.model_dump() for f in flights]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@flights_bp.route("/<int:flight_id>", methods=["GET"])
def get_flight(flight_id: int):
    try:
        flight = FlightService.get_flight_by_id(flight_id)
        return jsonify(flight.model_dump()), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404

@flights_bp.route("", methods=["POST"])
def create_flight():
    try:
        data = request.get_json()
        dto = CreateFlightDTO(**data)
        
        # TODO: Extract user_id from JWT token
        created_by_user_id = data.get("created_by_user_id", 1)  # Placeholder
        
        flight = FlightService.create_flight(dto, created_by_user_id)
        return jsonify(flight.model_dump()), 201
    except ValidationError as e:
        return jsonify({"error": e.errors()}), 400
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@flights_bp.route("/<int:flight_id>/approve", methods=["PUT"])
def approve_flight(flight_id: int):
    try:
        flight = FlightService.approve_flight(flight_id)
        return jsonify(flight.model_dump()), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404

@flights_bp.route("/<int:flight_id>/reject", methods=["PUT"])
def reject_flight(flight_id: int):
    try:
        data = request.get_json()
        reason = data.get("reason", "No reason provided")
        flight = FlightService.reject_flight(flight_id, reason)
        return jsonify(flight.model_dump()), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404

@flights_bp.route("/<int:flight_id>/cancel", methods=["PUT"])
def cancel_flight(flight_id: int):
    try:
        flight = FlightService.cancel_flight(flight_id)
        return jsonify(flight.model_dump()), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404

@flights_bp.route("/<int:flight_id>", methods=["DELETE"])
def delete_flight(flight_id: int):
    try:
        FlightService.delete_flight(flight_id)
        return jsonify({"message": "Flight deleted successfully"}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404