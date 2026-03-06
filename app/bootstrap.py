from __future__ import annotations

from app.db.migrations import bootstrap_database
from app.db.repository import Repository
from app.logging_config import setup_logging
from app.paths import ensure_paths


def bootstrap_app():
    ensure_paths()
    setup_logging()
    bootstrap_database()
    with Repository() as repo:
        settings = repo.get_settings()
        repo.save_settings(settings)
    return settings
