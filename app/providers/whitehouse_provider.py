from __future__ import annotations

import hashlib
import logging
from datetime import datetime

from bs4 import BeautifulSoup
from dateutil import parser as dtparser

from app.parsing.event_classifier import classify_event
from app.providers.provider_base import ProviderBase
from app.utils.http import build_client

log = logging.getLogger(__name__)


class WhiteHouseEventProvider(ProviderBase):
    url = "https://www.whitehouse.gov/briefing-room/statements-releases/"

    def __init__(self, timeout_seconds: int = 20) -> None:
        self.timeout_seconds = timeout_seconds

    def fetch(self) -> list[dict]:
        try:
            with build_client(self.timeout_seconds) as client:
                html = client.get(self.url).text
            soup = BeautifulSoup(html, "lxml")
            cards = soup.select("li.wp-block-post")[:25]
            rows = []
            for c in cards:
                title_el = c.select_one("h2 a")
                if not title_el:
                    continue
                title = title_el.get_text(" ", strip=True)
                if "trump" not in title.lower():
                    continue
                link = title_el.get("href", "")
                date_el = c.select_one("time")
                dt = dtparser.parse(date_el.get("datetime")) if date_el and date_el.get("datetime") else None
                ext = hashlib.md5((title + link).encode()).hexdigest()[:16]
                rows.append(
                    {
                        "external_id": f"wh_{ext}",
                        "title": title,
                        "event_datetime": dt,
                        "location": "",
                        "source_provider": "whitehouse",
                        "source_url": link,
                        "event_type": classify_event(title),
                        "topic_tags_json": "[]",
                        "entity_tags_json": "[]",
                        "likely_qualifying": True,
                        "source_confidence": 0.7,
                        "raw_payload_json": "{}",
                    }
                )
            return rows
        except Exception as exc:
            log.warning("WhiteHouse fetch failed: %s", exc)
            return [
                {
                    "external_id": "demo_event_1",
                    "title": "Demo Trump rally remarks",
                    "event_datetime": datetime.utcnow(),
                    "location": "Demo",
                    "source_provider": "demo",
                    "source_url": "",
                    "event_type": "rally",
                    "topic_tags_json": '["economy"]',
                    "entity_tags_json": '["Trump"]',
                    "likely_qualifying": True,
                    "source_confidence": 0.3,
                    "raw_payload_json": "{}",
                }
            ]
