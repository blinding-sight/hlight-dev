import smtplib
from email.message import EmailMessage
import os
from utils.logger import setup_logger

logger = setup_logger("notifier")

def send_notification(to_email: str, subject: str, body: str):
    """
    Send a simple notification email using Gmail SMTP.
    Requires:
      GMAIL_SMTP_USER
      GMAIL_SMTP_PASSWORD (App Password)
    """
    user = os.getenv("GMAIL_SMTP_USER")
    password = os.getenv("GMAIL_SMTP_PASSWORD")

    if not user or not password:
        logger.warning("SMTP credentials not set; skipping notification")
        return

    msg = EmailMessage()
    msg["From"] = user
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.set_content(body)

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(user, password)
            smtp.send_message(msg)
        logger.info(f"Notification sent to {to_email}")
    except Exception as e:
        logger.error(f"Failed to send notification: {e}")

if __name__ == "__main__":
    send_notification("test@example.com", "Test", "This is a test email")
