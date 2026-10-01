import pytest
from sqlalchemy.orm import Session

from app import container
from app.core.settings import Settings
from app.infra.clients.log_alert_notifier import LogAlertNotifier
from app.infra.clients.smtp_alert_notifier import SmtpAlertNotifier
from app.usecases.changelog_usecase import ChangelogUsecase


def test_uses_log_notifier_without_smtp_host(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(container, "settings", Settings(DATABASE_URL="sqlite://", SMTP_HOST=None))

    assert isinstance(container.get_alert_notifier(), LogAlertNotifier)


def test_uses_smtp_notifier_with_smtp_host(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(container, "settings", Settings(DATABASE_URL="sqlite://", SMTP_HOST="smtp.test"))

    assert isinstance(container.get_alert_notifier(), SmtpAlertNotifier)


def test_builds_changelog_usecase() -> None:
    assert isinstance(container.build_changelog_usecase(Session()), ChangelogUsecase)
