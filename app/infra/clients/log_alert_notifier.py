import logging
from typing import override

from app.domain.notifiers.alert_notifier import AlertNotifier

logger = logging.getLogger("uvicorn.error")


class LogAlertNotifier(AlertNotifier):
    @override
    def send(self, to_email: str, subject: str, body: str) -> None:
        logger.info("ALERT to %s | %s\n%s", to_email, subject, body)
