from __future__ import annotations

import logging

from sqlalchemy import select

from app.db.models import Event
from app.db.repository import Repository
from app.providers.whitehouse_provider import WhiteHouseEventProvider

log = logging.getLogger(__name__)


class EventService:
    def __init__(self, timeout_seconds: int = 20):
        self.provider = WhiteHouseEventProvider(timeout_seconds=timeout_seconds)

    def sync(self) -> int:
        rows = self.provider.fetch()
        with Repository() as repo:
            for r in rows:
                repo.upsert_event(r)
        log.info("Synced %s events", len(rows))
        return len(rows)

    def list_events(self) -> list[Event]:
        with Repository() as repo:
            return list(repo.session.scalars(select(Event).order_by(Event.event_datetime.desc().nullslast())))
