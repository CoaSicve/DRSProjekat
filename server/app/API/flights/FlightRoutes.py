from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt

from app.API.flights.FlightService import FlightService
from app.API.purchases.PurchaseService import PurchaseService
from app.Domain.models.User import User
from app.Extensions import db
from app.Helpers.authorization import require_admin, require_manager
from app.Services.EmailService import EmailService
from app.Services.PassengerMailTemplates import flight_cancelled_for_passenger_body

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


@flights_bp.route("/<int:flight_id>", methods=["PUT"])
@jwt_required()
def update_flight(flight_id: int):
    """Update flight - MANAGER only"""
    try:
        require_manager()
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        data = request.get_json() or {}

        flight = FlightService.update_flight(flight_id, data, token)
        return jsonify(flight), 200
    except PermissionError as e:
        return jsonify({"error": str(e)}), 403
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

        purchases = PurchaseService.get_purchases_by_flight(flight_id)
        flight = FlightService.cancel_flight(flight_id, token)

        for purchase in purchases:
            status = purchase.get("status")
            if status not in ("COMPLETED", "IN_PROGRESS"):
                continue

            user_id = purchase.get("user_id")
            ticket_price = purchase.get("ticket_price")
            if user_id is None or ticket_price is None:
                continue

            user = User.query.get(user_id)
            if not user:
                continue

            user.accountBalance += float(ticket_price)

            try:
                PurchaseService.cancel_purchase(purchase.get("id"))
            except Exception as e:
                print(f"Failed to cancel purchase {purchase.get('id')}: {e}")

            if user.email:
                try:
                    EmailService.send(
                        to=user.email,
                        subject="Flight cancelled",
                        body=flight_cancelled_for_passenger_body(flight)
                    )
                except Exception as e:
                    print(f"Failed to send cancellation email to user {user_id}: {e}")

        db.session.commit()
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
