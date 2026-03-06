from __future__ import annotations

import json
from datetime import datetime
from typing import Any

from sqlalchemy import delete, select

from app.config import AppSettings
from app.db.models import AppSetting, Event, JobRun, Market, Outcome, Prediction, Transcript, TranscriptMatch
from app.db.session import SessionLocal


class Repository:
    def __enter__(self) -> "Repository":
        self.session = SessionLocal()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        if exc:
            self.session.rollback()
        else:
            self.session.commit()
        self.session.close()

    def upsert_market(self, payload: dict[str, Any]) -> Market:
        m = self.session.scalar(select(Market).where(Market.external_id == payload["external_id"]))
        if not m:
            m = Market(external_id=payload["external_id"], first_seen_at=datetime.utcnow())
            self.session.add(m)
        for k, v in payload.items():
            setattr(m, k, v)
        m.last_seen_at = datetime.utcnow()
        return m

    def upsert_outcome(self, market_id: int, payload: dict[str, Any]) -> Outcome:
        o = self.session.scalar(
            select(Outcome).where(Outcome.market_id == market_id, Outcome.raw_label == payload["raw_label"])
        )
        if not o:
            o = Outcome(market_id=market_id, raw_label=payload["raw_label"], first_seen_at=datetime.utcnow())
            self.session.add(o)
        for k, v in payload.items():
            setattr(o, k, v)
        o.last_seen_at = datetime.utcnow()
        return o

    def upsert_event(self, payload: dict[str, Any]) -> Event:
        e = self.session.scalar(select(Event).where(Event.external_id == payload["external_id"]))
        if not e:
            e = Event(external_id=payload["external_id"], first_seen_at=datetime.utcnow())
            self.session.add(e)
        for k, v in payload.items():
            setattr(e, k, v)
        e.last_seen_at = datetime.utcnow()
        return e

    def upsert_transcript(self, event_id: int, payload: dict[str, Any]) -> Transcript:
        t = self.session.scalar(select(Transcript).where(Transcript.event_id == event_id))
        if not t:
            t = Transcript(event_id=event_id)
            self.session.add(t)
        for k, v in payload.items():
            setattr(t, k, v)
        t.updated_at = datetime.utcnow()
        return t

    def replace_prediction(self, outcome_id: int, payload: dict[str, Any]) -> Prediction:
        self.session.execute(delete(Prediction).where(Prediction.outcome_id == outcome_id))
        p = Prediction(outcome_id=outcome_id, **payload)
        self.session.add(p)
        return p

    def replace_match(self, transcript_id: int, outcome_id: int, payload: dict[str, Any]) -> TranscriptMatch:
        self.session.execute(
            delete(TranscriptMatch).where(
                TranscriptMatch.transcript_id == transcript_id, TranscriptMatch.outcome_id == outcome_id
            )
        )
        item = TranscriptMatch(transcript_id=transcript_id, outcome_id=outcome_id, **payload)
        self.session.add(item)
        return item

    def get_settings(self) -> AppSettings:
        rows = self.session.scalars(select(AppSetting)).all()
        as_dict = {r.key: json.loads(r.value_json) for r in rows}
        return AppSettings(**as_dict) if as_dict else AppSettings()

    def save_settings(self, settings: AppSettings) -> None:
        for key, value in settings.model_dump().items():
            row = self.session.get(AppSetting, key)
            if not row:
                row = AppSetting(key=key, value_json="null")
                self.session.add(row)
            row.value_json = json.dumps(value)
            row.updated_at = datetime.utcnow()

    def create_job(self, name: str) -> JobRun:
        j = JobRun(job_name=name, started_at=datetime.utcnow(), status="running")
        self.session.add(j)
        self.session.flush()
        return j

    def finish_job(self, job_id: int, status: str, details: dict[str, Any]) -> None:
        row = self.session.get(JobRun, job_id)
        if row:
            row.status = status
            row.details_json = json.dumps(details)
            row.finished_at = datetime.utcnow()
