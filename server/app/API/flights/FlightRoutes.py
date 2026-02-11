from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt

from app.API.flights.FlightService import FlightService
from app.Helpers.authorization import require_admin

flights_bp = Blueprint("flights", __name__, url_prefix="/api/v1/flights")


@flights_bp.route("", methods=["GET"])
def get_all_flights():
    """Get all flights - public endpoint"""
    try:
        flights = FlightService.get_all_flights()
        return jsonify(flights), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@flights_bp.route("/<int:flight_id>", methods=["GET"])
def get_flight(flight_id: int):
    """Get flight by ID - public endpoint"""
    try:
        flight = FlightService.get_flight_by_id(flight_id)
        return jsonify(flight), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@flights_bp.route("", methods=["POST"])
@jwt_required()
def create_flight():
    """Create flight - MANAGER only"""
    try:
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        data = request.get_json()
        
        flight = FlightService.create_flight(data, token)
        return jsonify(flight), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@flights_bp.route("/<int:flight_id>/approve", methods=["PUT"])
@jwt_required()
def approve_flight(flight_id: int):
    """Approve flight - ADMIN only"""
    try:
        require_admin()
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        
        flight = FlightService.approve_flight(flight_id, token)
        return jsonify(flight), 200
    except PermissionError as e:
        return jsonify({"error": str(e)}), 403
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@flights_bp.route("/<int:flight_id>/reject", methods=["PUT"])
@jwt_required()
def reject_flight(flight_id: int):
    """Reject flight - ADMIN only"""
    try:
        require_admin()
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        data = request.get_json() or {}
        
        flight = FlightService.reject_flight(flight_id, data, token)
        return jsonify(flight), 200
    except PermissionError as e:
        return jsonify({"error": str(e)}), 403
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@flights_bp.route("/<int:flight_id>/cancel", methods=["PUT"])
@jwt_required()
def cancel_flight(flight_id: int):
    """Cancel flight - ADMIN only"""
    try:
        require_admin()
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        
        flight = FlightService.cancel_flight(flight_id, token)
        return jsonify(flight), 200
    except PermissionError as e:
        return jsonify({"error": str(e)}), 403
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@flights_bp.route("/<int:flight_id>", methods=["DELETE"])
@jwt_required()
def delete_flight(flight_id: int):
    """Delete flight - ADMIN only"""
    try:
        require_admin()
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        
        flight = FlightService.delete_flight(flight_id, token)
        return jsonify(flight), 200
    except PermissionError as e:
        return jsonify({"error": str(e)}), 403
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
