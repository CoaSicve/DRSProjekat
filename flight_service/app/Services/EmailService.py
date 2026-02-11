from flask import current_app
from flask_mail import Message
from app.Extensions.mail import mail

class EmailService:
    @staticmethod
    def send(subject: str, body: str, to: str = None):
        enabled = current_app.config.get("MAIL_ENABLED", True)

        # podrži i bool i "true"/"false"
        if isinstance(enabled, str):
            enabled = enabled.strip().lower() == "true"

        if not enabled:
            return False

        default_to = current_app.config.get("MAIL_TEST_TO")
        recipient = to or default_to
        if not recipient:
            raise ValueError("Missing recipient (pass 'to' or set MAIL_TEST_TO)")

        msg = Message(subject=subject, recipients=[recipient], body=body)
        mail.send(msg)
        return True