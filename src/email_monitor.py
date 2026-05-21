import imaplib
import email
from email.header import decode_header
import os
from utils.logger import setup_logger
from utils.email_parser import parse_email_body

logger = setup_logger("email_monitor")

def _decode_mime_header(value: str) -> str:
    parts = decode_header(value)
    decoded = ""
    for text, enc in parts:
        if isinstance(text, bytes):
            decoded += text.decode(enc or "utf-8", errors="ignore")
        else:
            decoded += text
    return decoded

def fetch_clip_requests():
    """
    Connect to Gmail IMAP, fetch unread emails, parse them into clip requests.
    Requires:
      GMAIL_IMAP_USER
      GMAIL_IMAP_PASSWORD (App Password)
    """
    user = os.getenv("GMAIL_IMAP_USER")
    password = os.getenv("GMAIL_IMAP_PASSWORD")

    if not user or not password:
        logger.error("Missing GMAIL_IMAP_USER or GMAIL_IMAP_PASSWORD")
        return []

    logger.info("Connecting to Gmail IMAP")
    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(user, password)
    mail.select("INBOX")

    status, data = mail.search(None, "UNSEEN")
    if status != "OK":
        logger.error("Failed to search mailbox")
        return []

    ids = data[0].split()
    logger.info(f"Found {len(ids)} unread messages")

    results = []

    for msg_id in ids:
        status, msg_data = mail.fetch(msg_id, "(RFC822)")
        if status != "OK":
            logger.warning(f"Failed to fetch message {msg_id}")
            continue

        msg = email.message_from_bytes(msg_data[0][1])
        subject = _decode_mime_header(msg.get("Subject", ""))

        logger.info(f"Processing email: {subject}")

        # Extract plain text body
        body_text = ""
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    charset = part.get_content_charset() or "utf-8"
                    body_text = part.get_payload(decode=True).decode(charset, errors="ignore")
                    break
        else:
            charset = msg.get_content_charset() or "utf-8"
            body_text = msg.get_payload(decode=True).decode(charset, errors="ignore")

        parsed = parse_email_body(body_text)
        if parsed:
            results.append(parsed)
            mail.store(msg_id, "+FLAGS", "\\Seen")
        else:
            logger.warning("Could not parse email into clip request")

    mail.logout()
    return results

if __name__ == "__main__":
    print(fetch_clip_requests())
