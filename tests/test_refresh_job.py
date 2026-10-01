import threading

import pytest

from app.jobs import refresh_job


class FakeUsecase:
    def __init__(self, result: int | Exception) -> None:
        self.result = result

    def refresh_all(self) -> int:
        if isinstance(self.result, Exception):
            raise self.result
        return self.result


class FakeSession:
    closed = False

    def close(self) -> None:
        self.closed = True


@pytest.fixture
def session(monkeypatch: pytest.MonkeyPatch) -> FakeSession:
    fake = FakeSession()
    monkeypatch.setattr(refresh_job, "SessionLocal", lambda: fake)
    return fake


def test_refresh_once_logs_count_and_closes_session(
    monkeypatch: pytest.MonkeyPatch, session: FakeSession, caplog: pytest.LogCaptureFixture
) -> None:
    monkeypatch.setattr(refresh_job, "build_changelog_usecase", lambda db: FakeUsecase(3))

    with caplog.at_level("INFO", logger="uvicorn.error"):
        refresh_job.refresh_once()

    assert "3 new entries" in caplog.text
    assert session.closed


def test_refresh_once_swallows_errors_and_closes_session(
    monkeypatch: pytest.MonkeyPatch, session: FakeSession, caplog: pytest.LogCaptureFixture
) -> None:
    monkeypatch.setattr(refresh_job, "build_changelog_usecase", lambda db: FakeUsecase(RuntimeError("boom")))

    refresh_job.refresh_once()

    assert "Automatic refresh failed" in caplog.text
    assert session.closed


def test_loop_refreshes_each_tick_until_stopped(monkeypatch: pytest.MonkeyPatch) -> None:
    stop = threading.Event()
    calls: list[int] = []

    def fake_refresh() -> None:
        calls.append(1)
        if len(calls) == 2:
            stop.set()

    monkeypatch.setattr(refresh_job, "refresh_once", fake_refresh)

    refresh_job.run_refresh_loop(stop)

    assert len(calls) == 2


def test_loop_does_not_refresh_if_already_stopped() -> None:
    stop = threading.Event()
    stop.set()

    refresh_job.run_refresh_loop(stop)
