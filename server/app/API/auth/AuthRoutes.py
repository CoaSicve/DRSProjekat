from flask import Blueprint, request, jsonify
from pydantic import ValidationError

from app.Domain.DTOs import LoginUserDTO, RegistrationUserDTO
from app.API.auth.service import AuthService

auth_bp = Blueprint("auth", __name__, url_prefix="/api/v1")

@auth_bp.route("/login", methods=["POST"])
def login():
    try:
        dto = LoginUserDTO(**request.get_json())
        token = AuthService.login(dto)
        return jsonify({"access_token": token}), 200

    except ValidationError as e:
        return jsonify({"error": e.errors()}), 400

    except ValueError as e:
        return jsonify({"error": str(e)}), 401


@auth_bp.route("/register", methods=["POST"])
def register():
    try:
        dto = RegistrationUserDTO(**request.get_json())
        token = AuthService.register(dto)
        return jsonify({"access_token": token}), 201

    except ValidationError as e:
        return jsonify({"error": e.errors()}), 400

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
