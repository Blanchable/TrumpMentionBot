from __future__ import annotations

import logging

from bs4 import BeautifulSoup

from app.utils.http import build_client

log = logging.getLogger(__name__)


class TranscriptProvider:
    def __init__(self, timeout_seconds: int = 20):
        self.timeout_seconds = timeout_seconds

    def fetch_text(self, url: str) -> tuple[str, str, float]:
        if not url:
            return "missing", "", 0.0
        try:
            with build_client(self.timeout_seconds) as client:
                html = client.get(url).text
            soup = BeautifulSoup(html, "lxml")
            article = soup.select_one("article") or soup
            text = article.get_text(" ", strip=True)
            if len(text) < 40:
                return "empty", text, 0.2
            return "ok", text, 0.8
        except Exception as exc:
            log.warning("Transcript fetch failed: %s", exc)
            return "failed", "", 0.0
