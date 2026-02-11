from flask import Blueprint, jsonify, request
from app.API.purchases.PurchaseService import PurchaseService
from app.Extensions.db import db
from app.Domain.models.Purchase import Purchase

purchase_bp = Blueprint("purchase_bp", __name__)

@purchase_bp.route("/purchase", methods=["POST"])
def create_purchase():
    data = request.get_json()
    user_id = data.get("user_id")
    flight_id = data.get("flight_id")

    try:
        purchase = PurchaseService.start_purchase(user_id, flight_id)
        return jsonify({
            "message": "Kupovina zapoceta.",
            "purchase_id": purchase.id,
            "status": purchase.status.name
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@purchase_bp.route("/purchases/<int:user_id>", methods=["GET"])
def get_user_purchases(user_id):
    purchases = Purchase.query.filter_by(user_id=user_id).all()
    return jsonify([
        {
            "id": p.id,
            "flight_id": p.flight_id,
            "status": p.status.name,
            "ticket_price": p.ticket_price,
            "purchase_time": p.purchase_time.isoformat()
        } for p in purchases
    ])