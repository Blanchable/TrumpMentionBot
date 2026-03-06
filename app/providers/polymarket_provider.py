from __future__ import annotations

import json
import logging
from datetime import datetime

from app.providers.provider_base import ProviderBase
from app.utils.http import build_client

log = logging.getLogger(__name__)


class PolymarketProvider(ProviderBase):
    url = "https://gamma-api.polymarket.com/markets"

    def __init__(self, timeout_seconds: int = 20) -> None:
        self.timeout_seconds = timeout_seconds

    def fetch(self) -> list[dict]:
        params = {"active": "true", "closed": "false", "limit": 200}
        try:
            with build_client(self.timeout_seconds) as client:
                resp = client.get(self.url, params=params)
                resp.raise_for_status()
                raw = resp.json()
            rows = []
            for item in raw:
                title = (item.get("question") or "").strip()
                if "trump" not in title.lower():
                    continue
                outcomes = item.get("outcomes") or []
                prices = item.get("outcomePrices") or []
                for idx, out in enumerate(outcomes):
                    if str(out).upper() != "YES":
                        continue
                    yes_price = float(prices[idx]) if idx < len(prices) else 0.0
                    no_price = 1.0 - yes_price
                    rows.append(
                        {
                            "external_id": str(item.get("id") or item.get("conditionId")),
                            "title": title,
                            "slug": item.get("slug") or "",
                            "description": item.get("description") or "",
                            "rules_text": item.get("rules") or "",
                            "scope_type": "event" if "at" in title.lower() else "broader",
                            "source_provider": "polymarket",
                            "raw_payload_json": json.dumps(item),
                            "resolution_end_at": _parse_dt(item.get("endDate")),
                            "outcome": {
                                "raw_label": title,
                                "yes_price": yes_price,
                                "no_price": no_price,
                                "implied_probability": yes_price,
                            },
                        }
                    )
            return rows
        except Exception as exc:
            log.warning("Polymarket fetch failed: %s", exc)
            return []


def _parse_dt(value: str | None):
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).replace(tzinfo=None)
    except Exception:
        return None
