from app.extensions import db
from app.enums.UserRole import UserRole

class User(db.Model):
    __database__ = 'users_db'
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(80), nullable=False)
    lastName = db.Column(db.String(80), nullable=False)
    dateOfBirth = db.Column(db.Date, nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    role = db.Column(db.Enum(UserRole), nullable=False, default=UserRole.USER)
    password = db.Column(db.String(200), nullable=False)
    gender = db.Column(db.String(20), nullable=True)
    state = db.Column(db.String(50), nullable=True)
    street = db.Column(db.String(100), nullable=True)
    number = db.Column(db.String(20), nullable=True)
    accountBalance = db.Column(db.Float, nullable=False, default=0.0)
