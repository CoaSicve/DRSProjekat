from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity

from app.API.purchases.PurchaseService import PurchaseService
from app.Domain.models.User import User
from app.Extensions import db

purchase_bp = Blueprint("purchase_bp", __name__, url_prefix="/api/v1")


@purchase_bp.route("/purchase", methods=["POST"])
def create_purchase():
    data = request.get_json() or {}

    try:
        result = PurchaseService.create_purchase(data)
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@purchase_bp.route("/purchases/<int:user_id>", methods=["GET"])
def get_user_purchases(user_id: int):
    try:
        purchases = PurchaseService.get_user_purchases(user_id)
        return jsonify(purchases), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@purchase_bp.route("/purchases/<int:purchase_id>/cancel", methods=["PUT"])
@jwt_required()
def cancel_purchase(purchase_id: int):
    try:
        purchase = PurchaseService.get_purchase_by_id(purchase_id)
        purchase_user_id = purchase.get("user_id")
        ticket_price = purchase.get("ticket_price")
        status = purchase.get("status")

        if purchase_user_id is None or ticket_price is None:
            return jsonify({"error": "Invalid purchase data"}), 400

        claims = get_jwt()
        current_user_id = int(get_jwt_identity())
        if claims.get("role") != "ADMIN" and current_user_id != int(purchase_user_id):
            return jsonify({"error": "Access denied"}), 403

        if status == "CANCELLED":
            return jsonify(purchase), 200

        if status == "FAILED":
            return jsonify({"error": "Cannot cancel a failed purchase"}), 400

        user = User.query.get(purchase_user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404

        user.accountBalance += float(ticket_price)
        db.session.commit()

        try:
            updated_purchase = PurchaseService.cancel_purchase(purchase_id)
            return jsonify(updated_purchase), 200
        except ValueError as e:
            user.accountBalance -= float(ticket_price)
            db.session.commit()
            return jsonify({"error": str(e)}), 400
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500
