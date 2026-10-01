import smtplib
from email.message import EmailMessage

import pytest

from app.core.exceptions import NotifyError
from app.core.settings import Settings
from app.infra.clients.smtp_alert_notifier import SmtpAlertNotifier


class FakeSmtp:
    instances: list["FakeSmtp"] = []

    def __init__(self, host: str, port: int, timeout: int) -> None:
        self.host, self.port, self.timeout = host, port, timeout
        self.started_tls = False
        self.credentials: tuple[str, str] | None = None
        self.messages: list[EmailMessage] = []
        FakeSmtp.instances.append(self)

    def __enter__(self) -> "FakeSmtp":
        return self

    def __exit__(self, *args: object) -> None:
        return None

    def starttls(self) -> None:
        self.started_tls = True

    def login(self, username: str, password: str) -> None:
        self.credentials = (username, password)

    def send_message(self, message: EmailMessage) -> None:
        self.messages.append(message)


def make_settings(**overrides: object) -> Settings:
    values: dict[str, object] = {"DATABASE_URL": "sqlite://", "SMTP_HOST": "smtp.test", "SMTP_PORT": 2525}
    return Settings(**(values | overrides))  # ty: ignore[invalid-argument-type]


@pytest.fixture(autouse=True)
def fake_smtp(monkeypatch: pytest.MonkeyPatch) -> type[FakeSmtp]:
    FakeSmtp.instances = []
    monkeypatch.setattr(smtplib, "SMTP", FakeSmtp)
    return FakeSmtp


def test_sends_message_with_expected_headers(fake_smtp: type[FakeSmtp]) -> None:
    SmtpAlertNotifier(make_settings()).send("a@b.com", "Breaking", "body text")

    [server] = fake_smtp.instances
    [message] = server.messages
    assert (server.host, server.port) == ("smtp.test", 2525)
    assert message["To"] == "a@b.com"
    assert message["From"] == "alerts@apidrift.local"
    assert message["Subject"] == "Breaking"
    assert message.get_content().strip() == "body text"


def test_starttls_and_login_when_configured(fake_smtp: type[FakeSmtp]) -> None:
    settings = make_settings(SMTP_USERNAME="user", SMTP_PASSWORD="secret")

    SmtpAlertNotifier(settings).send("a@b.com", "s", "b")

    [server] = fake_smtp.instances
    assert server.started_tls
    assert server.credentials == ("user", "secret")


def test_skips_starttls_and_login_when_not_configured(fake_smtp: type[FakeSmtp]) -> None:
    SmtpAlertNotifier(make_settings(SMTP_STARTTLS=False)).send("a@b.com", "s", "b")

    [server] = fake_smtp.instances
    assert not server.started_tls
    assert server.credentials is None


@pytest.mark.parametrize("error", [smtplib.SMTPException("boom"), ConnectionRefusedError("down")])
def test_transport_errors_become_notify_error(monkeypatch: pytest.MonkeyPatch, error: Exception) -> None:
    def fail(self: FakeSmtp, message: EmailMessage) -> None:
        raise error

    monkeypatch.setattr(FakeSmtp, "send_message", fail)

    with pytest.raises(NotifyError):
        SmtpAlertNotifier(make_settings()).send("a@b.com", "s", "b")
