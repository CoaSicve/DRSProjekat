from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required

from server.app.API.users.UserService import UserService
from app.Helpers.authorization import require_self_or_admin, require_admin

users_bp = Blueprint("users", __name__, url_prefix="/api/v1/users")

@users_bp.route("", methods=["GET"])
@jwt_required()
def get_all_users():
    try:
        require_admin()
        users = UserService.get_all_users()
        return jsonify([user.model_dump() for user in users]), 200
    except PermissionError as e:
        return jsonify({"error": str(e)}), 403


@users_bp.route("/<int:user_id>", methods=["GET"])
@jwt_required()
def get_user_by_id(user_id: int):
    try:
        require_self_or_admin(user_id)
        user = UserService.get_user_by_id(user_id)
        return jsonify(user.model_dump()), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except PermissionError as e:
        return jsonify({"error": str(e)}), 403
