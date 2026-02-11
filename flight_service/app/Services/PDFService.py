import io
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from flask import current_app
from flask_mail import Message
from app.Services.EmailService import EmailService
from app.Extensions.mail import mail  

class PDFEmailService:
    @staticmethod
    def send_pdf(subject: str, body: str, to: str = None, pdf_filename: str = "document.pdf", pdf_content: str = None):
        """
        Generate a PDF and send it via email.

        :param subject: Email subject
        :param body: Email body
        :param to: Recipient email
        :param pdf_filename: Name of the PDF file
        :param pdf_content: Text content to include in PDF
        """
        
        pdf_buffer = io.BytesIO()
        c = canvas.Canvas(pdf_buffer, pagesize=A4)
        width, height = A4

        # PDF
        pdf_text = pdf_content or "This is a test PDF"
        text_object = c.beginText(40, height - 50)
        text_object.setFont("Helvetica", 12)
        for line in pdf_text.splitlines():
            text_object.textLine(line)
        c.drawText(text_object)
        c.showPage()
        c.save()

        pdf_buffer.seek(0)  

        # EMail
        enabled = current_app.config.get("MAIL_ENABLED", True)
        if isinstance(enabled, str):
            enabled = enabled.strip().lower() == "true"
        if not enabled:
            return False

        default_to = current_app.config.get("MAIL_TEST_TO")
        recipient = to or default_to
        if not recipient:
            raise ValueError("Missing recipient")

        msg = Message(subject=subject, recipients=[recipient], body=body)
        msg.attach(pdf_filename, "application/pdf", pdf_buffer.read())

        mail.send(msg)
        return True