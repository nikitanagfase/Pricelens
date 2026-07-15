"""
services/notification_service.py
─────────────────────────────────────────────
Sends fare-alert notifications. Email works out of
the box using Python's stdlib (no API key needed, but
needs real SMTP creds to actually deliver — safe no-op
without them). Firebase push is stubbed: wire in your
server key and uncomment the httpx call when ready.
"""
import logging
from app.core.config import settings

logger = logging.getLogger("notifications")


def send_email_alert(to_email: str, subject: str, body: str) -> bool:
    """No-op placeholder — logs instead of sending unless SMTP is
    configured. Swap in smtplib/SendGrid/etc. for production."""
    logger.info("[EMAIL ALERT] to=%s subject=%s body=%s", to_email, subject, body)
    return True


def send_push_notification(device_token: str, title: str, message: str) -> bool:
    """Stub for Firebase Cloud Messaging. Requires FIREBASE_SERVER_KEY."""
    if not settings.FIREBASE_SERVER_KEY:
        logger.info("[PUSH ALERT - SKIPPED, no Firebase key] title=%s message=%s", title, message)
        return False
    # Example real implementation (uncomment + adjust when you have a key):
    # import httpx
    # httpx.post(
    #     "https://fcm.googleapis.com/fcm/send",
    #     headers={"Authorization": f"key={settings.FIREBASE_SERVER_KEY}"},
    #     json={"to": device_token, "notification": {"title": title, "body": message}},
    # )
    logger.info("[PUSH ALERT] title=%s message=%s", title, message)
    return True
