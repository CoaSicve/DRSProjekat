from flask_jwt_extended import create_access_token, get_jwt_identity, get_jwt

def build_claims(user):
    return {
        "id": user.id,
        "email": user.email,
        "role": user.role.value
    }

def create_user_token(user) -> str:
    claims = build_claims(user)
    access_token = create_access_token(identity=user.id, additional_claims=claims)
    return access_token

def get_current_user_id() -> int:
    return get_jwt_identity()

def get_current_user_claims() -> dict:
    return get_jwt()

def get_current_user_role() -> str:
    claims = get_current_user_claims()
    return claims.get("role")

def get_current_user_email() -> str:
    claims = get_current_user_claims()
    return claims.get("email")