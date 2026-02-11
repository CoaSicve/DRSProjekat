from flask import Blueprint, jsonify, request, current_app
from flask_mail import Message
from app.Extensions.mail import mail

test_mail_bp = Blueprint("test_mail", __name__, url_prefix="/api/v1")


@test_mail_bp.get("/test-mail")
def test_mail():
    # prima ?to=... ili koristi MAIL_TEST_TO iz .env
    to = request.args.get("to") or current_app.config.get("MAIL_TEST_TO")
    if not to:
        return jsonify({
            "ok": False,
            "error": "Missing recipient. Provide ?to=someone@example.com or set MAIL_TEST_TO in .env"
        }), 400

    msg = Message(
        subject="DRS Flight Service - test mail ✅",
        recipients=[to],
        body="Ako si dobio ovu poruku, Flask-Mail radi kako treba.",
    )

    try:
        mail.send(msg)
        return jsonify({"ok": True, "sent_to": to})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500