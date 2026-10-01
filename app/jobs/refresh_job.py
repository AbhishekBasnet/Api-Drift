import logging
import threading

from app.container import build_changelog_usecase
from app.core.database import SessionLocal
from app.core.settings import settings

logger = logging.getLogger("uvicorn.error")


def refresh_once() -> None:
    db = SessionLocal()
    try:
        new_entries = build_changelog_usecase(db).refresh_all()
        logger.info("Automatic refresh finished: %d new entries", new_entries)
    except Exception:
        logger.exception("Automatic refresh failed")
    finally:
        db.close()


def run_refresh_loop(stop: threading.Event) -> None:
    while not stop.wait(settings.REFRESH_INTERVAL_SECONDS):
        refresh_once()
