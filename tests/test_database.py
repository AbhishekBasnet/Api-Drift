import pytest

from app.core import database


def test_get_db_yields_session_and_closes_it(monkeypatch: pytest.MonkeyPatch) -> None:
    closed: list[bool] = []

    class FakeSession:
        def close(self) -> None:
            closed.append(True)

    monkeypatch.setattr(database, "SessionLocal", FakeSession)

    generator = database.get_db()
    assert isinstance(next(generator), FakeSession)
    assert not closed

    generator.close()
    assert closed == [True]
