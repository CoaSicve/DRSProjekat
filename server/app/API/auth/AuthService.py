from app.Extensions import db
from app.Domain.models.User import User
from app.Helpers.hasher import hash_password, verify_password
from app.Helpers.jwt_utils import create_user_token
from app.Domain.enums.UserRole import UserRole

class AuthService:

    @staticmethod
    def login(dto):
        user = User.query.filter_by(email=dto.email).first()

        if not user:
            raise ValueError("Invalid email or password")

        if not verify_password(user.password, dto.password):
            raise ValueError("Invalid email or password")

        return create_user_token(user)


    @staticmethod
    def register(dto):
        existing_user = User.query.filter_by(email=dto.email).first()
        if existing_user:
            raise ValueError("Email already registered")

        user = User(
            name=dto.name,
            lastName=dto.lastName,
            dateOfBirth=dto.dateOfBirth,
            email=dto.email,
            role=UserRole.USER,
            password=hash_password(dto.password),
            gender=dto.gender,
            state=dto.state,
            street=dto.street,
            number=dto.number,
            accountBalance=dto.accountBalance,
            profileImage=None
        )

        db.session.add(user)
        db.session.commit()

        return create_user_token(user)
