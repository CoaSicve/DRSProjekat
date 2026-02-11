from flask import Blueprint, jsonify, request

from app.API.purchases.PurchaseService import PurchaseService

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
