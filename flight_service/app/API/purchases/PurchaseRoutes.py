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
    user_email = data.get("user_email")

    try:
        purchase = PurchaseService.start_purchase(user_id, flight_id, user_email)
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

@purchase_bp.route("/purchases/by-id/<int:purchase_id>", methods=["GET"])
def get_purchase_by_id(purchase_id):
    purchase = Purchase.query.get(purchase_id)
    if not purchase:
        return jsonify({"error": "Purchase not found"}), 404
    return jsonify({
        "id": purchase.id,
        "user_id": purchase.user_id,
        "flight_id": purchase.flight_id,
        "status": purchase.status.name,
        "ticket_price": purchase.ticket_price,
        "purchase_time": purchase.purchase_time.isoformat()
    })

@purchase_bp.route("/purchases/by-flight/<int:flight_id>", methods=["GET"])
def get_purchases_by_flight(flight_id):
    purchases = Purchase.query.filter_by(flight_id=flight_id).all()
    return jsonify([
        {
            "id": p.id,
            "user_id": p.user_id,
            "flight_id": p.flight_id,
            "status": p.status.name,
            "ticket_price": p.ticket_price,
            "purchase_time": p.purchase_time.isoformat()
        } for p in purchases
    ])

@purchase_bp.route("/purchases/<int:purchase_id>/cancel", methods=["PUT"])
def cancel_purchase(purchase_id):
    try:
        purchase = PurchaseService.cancel_purchase(purchase_id)
        return jsonify({
            "id": purchase.id,
            "user_id": purchase.user_id,
            "flight_id": purchase.flight_id,
            "status": purchase.status.name,
            "ticket_price": purchase.ticket_price,
            "purchase_time": purchase.purchase_time.isoformat()
        }), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400