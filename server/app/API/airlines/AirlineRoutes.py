from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from app.API.airlines.AirlineService import AirlineService
from app.Helpers.authorization import require_admin

airlines_bp = Blueprint("airlines", __name__, url_prefix="/api/v1/airlines")


@airlines_bp.route("", methods=["GET"])
def get_all_airlines():
    """Get all airlines - public endpoint"""
    try:
        airlines = AirlineService.get_all_airlines()
        return jsonify(airlines), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@airlines_bp.route("/<int:airline_id>", methods=["GET"])
def get_airline(airline_id: int):
    """Get airline by ID - public endpoint"""
    try:
        airline = AirlineService.get_airline_by_id(airline_id)
        return jsonify(airline), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@airlines_bp.route("", methods=["POST"])
@jwt_required()
def create_airline():
    """Create airline - ADMIN only"""
    try:
        require_admin()
        data = request.get_json()
        
        airline = AirlineService.create_airline(data)
        return jsonify(airline), 201
    except PermissionError as e:
        return jsonify({"error": str(e)}), 403
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@airlines_bp.route("/<int:airline_id>", methods=["DELETE"])
@jwt_required()
def delete_airline(airline_id: int):
    """Delete airline - ADMIN only"""
    try:
        require_admin()
        
        airline = AirlineService.delete_airline(airline_id)
        return jsonify(airline), 200
    except PermissionError as e:
        return jsonify({"error": str(e)}), 403
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
