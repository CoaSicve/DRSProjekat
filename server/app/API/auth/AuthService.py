import os
from app.Extensions import db
from app.Domain.models.User import User
from app.Helpers.hasher import hash_password, verify_password
from app.Helpers.jwt_utils import create_user_token
from app.Domain.enums.UserRole import UserRole
from datetime import datetime, timedelta
from flask import json, request

failed_attempts = {}  # {ip: attempts}
blocked_ips = {}  # {ip: locked_until_datetime}

class AuthService:
    MAX_LOGIN_ATTEMPTS = 3
    LOCK_DURATION = 60

    @staticmethod
    def load_admins():
        admins_path = os.path.join(os.getcwd(), "app", "config", "admins.json")
        if not os.path.exists(admins_path):
            return []

        with open(admins_path, "r") as f:
            return json.load(f)

    @staticmethod
    def _get_client_ip():
        """Get client IP address from request"""
        if request.headers.get('X-Forwarded-For'):
            return request.headers.get('X-Forwarded-For').split(',')[0].strip()
        return request.remote_addr

    @staticmethod
    def login(dto):
        global failed_attempts, blocked_ips

        client_ip = AuthService._get_client_ip()

        if client_ip in blocked_ips:
            if blocked_ips[client_ip] > datetime.utcnow():
                remaining = (blocked_ips[client_ip] - datetime.utcnow()).total_seconds()
                raise ValueError(f"IP address is temporarily blocked. Try again in {int(remaining)} seconds.")
            else:
                del blocked_ips[client_ip]
                failed_attempts[client_ip] = 0

        admins = AuthService.load_admins()
        print(f"Loaded admins: {admins}")
        for admin in admins:
            if admin["email"] == dto.email:
                if not verify_password(admin["password"], dto.password):
                    break 

                failed_attempts[client_ip] = 0
                print(f"Admin {admin['email']} logged in successfully.")
                return create_user_token(User(
                    id=admin.get("id", -1),
                    email=admin["email"],
                    name=admin["name"],
                    role=UserRole.ADMIN
                ))

        user = User.query.filter_by(email=dto.email).first()

        if not user or not verify_password(user.password, dto.password):
            failed_attempts[client_ip] = failed_attempts.get(client_ip, 0) + 1

            if failed_attempts[client_ip] >= AuthService.MAX_LOGIN_ATTEMPTS:
                blocked_ips[client_ip] = datetime.utcnow() + timedelta(seconds=AuthService.LOCK_DURATION)
                raise ValueError(f"Too many failed login attempts from this IP. Blocked for {AuthService.LOCK_DURATION} seconds.")

            raise ValueError("Invalid email or password")

        failed_attempts[client_ip] = 0
        blocked_ips.pop(client_ip, None)

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
