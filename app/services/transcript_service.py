from __future__ import annotations

import logging
from datetime import datetime

from sqlalchemy import select

from app.db.models import Event, Transcript
from app.db.repository import Repository
from app.parsing.text_normalizer import normalize_text
from app.providers.transcript_provider import TranscriptProvider

log = logging.getLogger(__name__)


class TranscriptService:
    def __init__(self, timeout_seconds: int = 20):
        self.provider = TranscriptProvider(timeout_seconds=timeout_seconds)

    def sync(self) -> int:
        count = 0
        with Repository() as repo:
            events = list(repo.session.scalars(select(Event).order_by(Event.event_datetime.desc().nullslast()).limit(20)))
            for event in events:
                status, text, quality = self.provider.fetch_text(event.source_url)
                cleaned, normalized = normalize_text(text)
                repo.upsert_transcript(
                    event.id,
                    {
                        "source_provider": "official",
                        "source_url": event.source_url,
                        "fetch_status": status,
                        "quality_score": quality,
                        "is_timestamped": False,
                        "original_text": text,
                        "cleaned_text": cleaned,
                        "normalized_text": normalized,
                        "fetch_error": "" if status == "ok" else status,
                        "fetched_at": datetime.utcnow(),
                    },
                )
                count += 1
        log.info("Transcript sync processed %s events", count)
        return count

    def list_transcripts(self) -> list[tuple[Transcript, Event]]:
        with Repository() as repo:
            rows = repo.session.execute(select(Transcript, Event).join(Event, Event.id == Transcript.event_id)).all()
            return rows
