import smtplib
from email.message import EmailMessage
from typing import override

from app.core.exceptions import NotifyError
from app.core.settings import Settings
from app.domain.notifiers.alert_notifier import AlertNotifier


class SmtpAlertNotifier(AlertNotifier):
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    @override
    def send(self, to_email: str, subject: str, body: str) -> None:
        message = EmailMessage()
        message["From"] = self.settings.ALERT_FROM_EMAIL
        message["To"] = to_email
        message["Subject"] = subject
        message.set_content(body)
        try:
            with smtplib.SMTP(self.settings.SMTP_HOST, self.settings.SMTP_PORT, timeout=10) as server:
                if self.settings.SMTP_STARTTLS:
                    server.starttls()
                if self.settings.SMTP_USERNAME and self.settings.SMTP_PASSWORD:
                    server.login(self.settings.SMTP_USERNAME, self.settings.SMTP_PASSWORD)
                server.send_message(message)
        except (smtplib.SMTPException, OSError) as exc:
            raise NotifyError(f"Could not send alert to {to_email}") from exc
