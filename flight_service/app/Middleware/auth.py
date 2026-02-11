from functools import wraps
from flask import request, jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity, get_jwt

def jwt_required_custom(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request()
            return fn(*args, **kwargs)
        except Exception as e:
            return jsonify({"error": "Invalid or missing token", "details": str(e)}), 401
    return wrapper

def get_current_user():
    """Izvlači user_id i email iz JWT tokena"""
    try:
        verify_jwt_in_request()
        claims = get_jwt()
        user_id = get_jwt_identity()
        email = claims.get("email")
        role = claims.get("role")
        
        return {
            "user_id": user_id,
            "email": email,
            "role": role
        }
    except Exception as e:
        return None

def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            print("admin_required: Verifying JWT...")
            verify_jwt_in_request()
            claims = get_jwt()
            print(f"admin_required: Got claims: {claims}")
            role = claims.get("role")
            print(f"admin_required: Role extracted: {role}")
            
            if role != "ADMIN":
                print(f"admin_required: User is not ADMIN (role={role})")
                return jsonify({"error": "Admin access required"}), 403
            
            print("admin_required: JWT verification successful, user is ADMIN")
            return fn(*args, **kwargs)
        except Exception as e:
            print(f"admin_required: Exception during JWT verification: {str(e)}")
            return jsonify({"error": "Invalid or missing token"}), 401
    return wrapper

def manager_required(fn):  # 🆕 DODATO
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request()
            claims = get_jwt()
            role = claims.get("role")
            
            if role != "MANAGER":
                return jsonify({"error": "Manager access required"}), 403
            
            return fn(*args, **kwargs)
        except Exception as e:
            return jsonify({"error": "Invalid or missing token"}), 401
    return wrapper

def manager_or_admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request()
            claims = get_jwt()
            role = claims.get("role")
            
            if role not in ["MANAGER", "ADMIN"]:
                return jsonify({"error": "Manager or Admin access required"}), 403
            
            return fn(*args, **kwargs)
        except Exception as e:
            return jsonify({"error": "Invalid or missing token"}), 401
    return wrapper