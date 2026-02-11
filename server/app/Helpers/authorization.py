from flask_jwt_extended import get_jwt_identity, get_jwt
from app.Domain.enums.UserRole import UserRole

def require_admin():
    claims = get_jwt()
    if claims.get("role") != UserRole.ADMIN.value:
        raise PermissionError("Admin access required")
    
def require_manager():
    claims = get_jwt()
    if claims.get("role") != UserRole.MANAGER.value:
        raise PermissionError("Manager access required")

def require_self_or_admin(user_id: int):
    claims = get_jwt()
    current_user_id = int(get_jwt_identity())
    role = claims.get("role")
    print(f"Current user ID: {current_user_id}, Role: {role}, Target user ID: {user_id}")

    if role == UserRole.ADMIN.value:
        return

    if current_user_id == user_id:
        return

    raise PermissionError("Access denied")
