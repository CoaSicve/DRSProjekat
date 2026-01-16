from app.Domain.models.User import User
from app.Domain.DTOs import UserDTO

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
    def _to_dto(user: User) -> UserDTO:
        return UserDTO(
            id=user.id,
            name=user.name,
            lastName=user.lastName,
            email=user.email,
            role=user.role.value,
            profileImage=user.profileImage
        )
