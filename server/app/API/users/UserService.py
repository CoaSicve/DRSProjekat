from app.Extensions import db
from app.Domain.models.User import User
from app.Domain.DTOs import UserDTO
from app.Domain.enums.UserRole import UserRole

class UserService:

    @staticmethod
    def get_all_users():
        users = User.query.all()
        return [UserService._to_dto(user) for user in users]

    @staticmethod
    def get_user_by_id(user_id: int):
        user = User.query.get(user_id)
        if not user:
            raise ValueError("User not found")
        return UserService._to_dto(user)

    @staticmethod
    def delete_user(user_id: int):
        user = User.query.get(user_id)
        if not user:
            raise ValueError("User not found")
        db.session.delete(user)
        db.session.commit()

    @staticmethod
    def update_user_role(user_id: int, role: str):
        user = User.query.get(user_id)
        if not user:
            raise ValueError("User not found")
        
        try:
            user.role = UserRole[role.upper()]
            db.session.commit()
            return UserService._to_dto(user)
        except KeyError:
            raise ValueError(f"Invalid role: {role}")

    @staticmethod
    def update_user_profile(user_id: int, data: dict):
        user = User.query.get(user_id)
        if not user:
            raise ValueError("User not found")
        
        # Update allowed fields
        allowed_fields = ['name', 'lastName', 'dateOfBirth', 'gender', 'state', 'street', 'number', 'profileImage']
        for field in allowed_fields:
            if field in data:
                # Convert empty strings to None for optional fields
                value = data[field]
                if isinstance(value, str) and value.strip() == '':
                    value = None
                setattr(user, field, value)
        
        db.session.commit()
        return UserService._to_dto(user)

    @staticmethod
    def _to_dto(user: User) -> UserDTO:
        return UserDTO(
            id=user.id,
            name=user.name,
            lastName=user.lastName,
            email=user.email,
            role=user.role.value,
            profileImage=user.profileImage
        )
