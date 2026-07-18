"""
notifier.py
-----------
Notification dispatch layer. Demo mode logs to console + DB.
Extend send() to plug in real channels (Twilio SMS, SMTP email, Pushbullet,
Telegram bot, etc.) using environment variables for credentials.
"""
from src.database import log_event


class Notifier:
    def __init__(self, channels=None):
        # channels could be ["console", "email", "sms"] in a real deployment
        self.channels = channels or ["console"]

    def send(self, title: str, message: str, severity: str = "warning"):
        if "console" in self.channels:
            print(f"[ALERT:{severity.upper()}] {title} - {message}")

        # Placeholder hooks for real integrations:
        # if "email" in self.channels: self._send_email(title, message)
        # if "sms" in self.channels: self._send_sms(title, message)

        log_event(source="notifier", event_type=title, detail=message, severity=severity)

    def _send_email(self, title, message):
        """Wire up smtplib + env vars (SMTP_HOST, SMTP_USER, SMTP_PASS) here."""
        raise NotImplementedError

    def _send_sms(self, title, message):
        """Wire up Twilio client + env vars (TWILIO_SID, TWILIO_TOKEN) here."""
        raise NotImplementedError
