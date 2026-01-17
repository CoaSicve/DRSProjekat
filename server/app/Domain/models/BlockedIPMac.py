from app.Extensions import db
from datetime import datetime

class BlockedIPMac(db.Model):
    __tablename__ = 'blocked_ip_mac'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ip_address = db.Column(db.String(45), nullable=True, index=True)  # IPv4 or IPv6
    mac_address = db.Column(db.String(17), nullable=True, index=True)  # MAC format: XX:XX:XX:XX:XX:XX
    failed_attempts = db.Column(db.Integer, nullable=False, default=0)
    locked_until = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
