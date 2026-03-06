from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Market(Base):
    __tablename__ = "markets"
    id: Mapped[int] = mapped_column(primary_key=True)
    external_id: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(500))
    slug: Mapped[str] = mapped_column(String(500), default="")
    description: Mapped[str] = mapped_column(Text, default="")
    rules_text: Mapped[str] = mapped_column(Text, default="")
    scope_type: Mapped[str] = mapped_column(String(64), default="broader")
    source_provider: Mapped[str] = mapped_column(String(64), default="polymarket")
    raw_payload_json: Mapped[str] = mapped_column(Text, default="{}")
    first_seen_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    last_seen_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    resolution_start_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    resolution_end_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    outcomes: Mapped[list[Outcome]] = relationship(back_populates="market", cascade="all, delete-orphan")


class Outcome(Base):
    __tablename__ = "outcomes"
    id: Mapped[int] = mapped_column(primary_key=True)
    market_id: Mapped[int] = mapped_column(ForeignKey("markets.id"), index=True)
    raw_label: Mapped[str] = mapped_column(String(500), default="")
    canonical_term: Mapped[str] = mapped_column(String(255), index=True)
    threshold_type: Mapped[str] = mapped_column(String(64), default="single")
    threshold_value: Mapped[int] = mapped_column(Integer, default=1)
    alias_json: Mapped[str] = mapped_column(Text, default="[]")
    yes_price: Mapped[float] = mapped_column(Float, default=0.0)
    no_price: Mapped[float] = mapped_column(Float, default=0.0)
    implied_probability: Mapped[float] = mapped_column(Float, default=0.0)
    notes_json: Mapped[str] = mapped_column(Text, default="{}")
    first_seen_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    last_seen_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    market: Mapped[Market] = relationship(back_populates="outcomes")


class Event(Base):
    __tablename__ = "events"
    id: Mapped[int] = mapped_column(primary_key=True)
    external_id: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(500))
    event_datetime: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    location: Mapped[str] = mapped_column(String(255), default="")
    source_provider: Mapped[str] = mapped_column(String(64), default="whitehouse")
    source_url: Mapped[str] = mapped_column(String(1000), default="")
    event_type: Mapped[str] = mapped_column(String(64), default="speech")
    topic_tags_json: Mapped[str] = mapped_column(Text, default="[]")
    entity_tags_json: Mapped[str] = mapped_column(Text, default="[]")
    likely_qualifying: Mapped[bool] = mapped_column(Boolean, default=True)
    source_confidence: Mapped[float] = mapped_column(Float, default=0.5)
    raw_payload_json: Mapped[str] = mapped_column(Text, default="{}")
    first_seen_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    last_seen_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Transcript(Base):
    __tablename__ = "transcripts"
    id: Mapped[int] = mapped_column(primary_key=True)
    event_id: Mapped[int] = mapped_column(ForeignKey("events.id"), index=True)
    source_provider: Mapped[str] = mapped_column(String(64), default="official")
    source_url: Mapped[str] = mapped_column(String(1000), default="")
    fetch_status: Mapped[str] = mapped_column(String(64), default="pending")
    quality_score: Mapped[float] = mapped_column(Float, default=0.0)
    is_timestamped: Mapped[bool] = mapped_column(Boolean, default=False)
    original_text: Mapped[str] = mapped_column(Text, default="")
    cleaned_text: Mapped[str] = mapped_column(Text, default="")
    normalized_text: Mapped[str] = mapped_column(Text, default="")
    fetch_error: Mapped[str] = mapped_column(Text, default="")
    fetched_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class TranscriptMatch(Base):
    __tablename__ = "transcript_matches"
    id: Mapped[int] = mapped_column(primary_key=True)
    transcript_id: Mapped[int] = mapped_column(ForeignKey("transcripts.id"), index=True)
    outcome_id: Mapped[int] = mapped_column(ForeignKey("outcomes.id"), index=True)
    raw_count: Mapped[int] = mapped_column(Integer, default=0)
    adjusted_count: Mapped[int] = mapped_column(Integer, default=0)
    matched_spans_json: Mapped[str] = mapped_column(Text, default="[]")
    ambiguous_spans_json: Mapped[str] = mapped_column(Text, default="[]")
    notes_json: Mapped[str] = mapped_column(Text, default="{}")
    analyzed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Prediction(Base):
    __tablename__ = "predictions"
    id: Mapped[int] = mapped_column(primary_key=True)
    outcome_id: Mapped[int] = mapped_column(ForeignKey("outcomes.id"), index=True)
    related_event_id: Mapped[int | None] = mapped_column(ForeignKey("events.id"), nullable=True)
    market_probability: Mapped[float] = mapped_column(Float, default=0.0)
    model_probability: Mapped[float] = mapped_column(Float, default=0.0)
    edge: Mapped[float] = mapped_column(Float, default=0.0)
    confidence_score: Mapped[float] = mapped_column(Float, default=0.0)
    component_scores_json: Mapped[str] = mapped_column(Text, default="{}")
    reason_summary: Mapped[str] = mapped_column(Text, default="")
    predicted_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class AppSetting(Base):
    __tablename__ = "app_settings"
    key: Mapped[str] = mapped_column(String(120), primary_key=True)
    value_json: Mapped[str] = mapped_column(Text)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class JobRun(Base):
    __tablename__ = "job_runs"
    id: Mapped[int] = mapped_column(primary_key=True)
    job_name: Mapped[str] = mapped_column(String(120), index=True)
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="running")
    details_json: Mapped[str] = mapped_column(Text, default="{}")
