from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class AppSettings(BaseModel):
    data_dir: str = "data"
    db_path: str = "data/trump_mentions.db"
    logs_dir: str = "logs"
    markets_refresh_minutes: int = 30
    events_refresh_minutes: int = 60
    transcripts_refresh_minutes: int = 120
    model_refresh_minutes: int = 60
    max_http_retries: int = 3
    request_timeout_seconds: int = 20
    enable_background_sync: bool = False
    enabled_market_provider_polymarket: bool = True
    enabled_event_provider_whitehouse: bool = True
    enabled_transcript_provider_official: bool = True
    use_demo_fallback_data_if_live_fetch_fails: bool = True


def dict_to_settings(values: dict[str, Any]) -> AppSettings:
    return AppSettings(**values)
