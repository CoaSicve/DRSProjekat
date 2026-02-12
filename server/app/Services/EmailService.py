import smtplib
from email.mime.text import MIMEText
from flask import current_app

class EmailService:
    @staticmethod
    def send(to: str, subject: str, body: str):
        # ako u config staviš bool, ovo radi i za bool i za string
        enabled = current_app.config.get("MAIL_ENABLED", True)
        if isinstance(enabled, str):
            enabled = enabled.lower() == "true"
        if not enabled:
            return

        msg = MIMEText(body, "html", "utf-8")
        msg["Subject"] = subject
        msg["From"] = current_app.config.get("MAIL_DEFAULT_SENDER")
        msg["To"] = to

        server = smtplib.SMTP(current_app.config.get("MAIL_SERVER"), int(current_app.config.get("MAIL_PORT", 587)))
        if str(current_app.config.get("MAIL_USE_TLS", "true")).lower() == "true":
            server.starttls()

        server.login(current_app.config.get("MAIL_USERNAME"), current_app.config.get("MAIL_PASSWORD"))
        server.sendmail(msg["From"], [to], msg.as_string())
        server.quit()