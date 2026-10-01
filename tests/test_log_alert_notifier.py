import pytest

from app.infra.clients.log_alert_notifier import LogAlertNotifier


def test_send_logs_recipient_subject_and_body(caplog: pytest.LogCaptureFixture) -> None:
    with caplog.at_level("INFO", logger="uvicorn.error"):
        LogAlertNotifier().send("a@b.com", "Breaking change", "Removed client_id")

    assert "a@b.com" in caplog.text
    assert "Breaking change" in caplog.text
    assert "Removed client_id" in caplog.text
