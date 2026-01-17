from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from app.API.users.UserService import UserService
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


@users_bp.route("/<int:user_id>", methods=["DELETE"])
@jwt_required()
def delete_user(user_id: int):
    try:
        require_admin()
        UserService.delete_user(user_id)
        return jsonify({"message": "User deleted successfully"}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except PermissionError as e:
        return jsonify({"error": str(e)}), 403


@users_bp.route("/<int:user_id>/role", methods=["PUT"])
@jwt_required()
def update_user_role(user_id: int):
    try:
        require_admin()
        data = request.get_json()
        role = data.get("role")
        
        if not role:
            return jsonify({"error": "Role is required"}), 400
        
        user = UserService.update_user_role(user_id, role)
        return jsonify(user.model_dump()), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except PermissionError as e:
        return jsonify({"error": str(e)}), 403


@users_bp.route("/<int:user_id>", methods=["PUT"])
@jwt_required()
def update_user_profile(user_id: int):
    try:
        require_self_or_admin(user_id)
        data = request.get_json()
        user = UserService.update_user_profile(user_id, data)
        return jsonify(user.model_dump()), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except PermissionError as e:
        return jsonify({"error": str(e)}), 403
