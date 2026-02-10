from flask_mail import Message
from app.Extensions.mail import mail

class EmailService:
    @staticmethod
    def send_email(subject: str, recipients: list[str], body: str):
        msg = Message(subject=subject, recipients=recipients, body=body)
        mail.send(msg)