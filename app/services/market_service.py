from __future__ import annotations

import json
import logging
from datetime import datetime

from sqlalchemy import select

from app.db.models import Market, Outcome
from app.db.repository import Repository
from app.parsing.rule_parser import parse_rule
from app.providers.polymarket_provider import PolymarketProvider

log = logging.getLogger(__name__)


class MarketService:
    def __init__(self, timeout_seconds: int = 20):
        self.provider = PolymarketProvider(timeout_seconds=timeout_seconds)

    def sync(self) -> int:
        rows = self.provider.fetch()
        if not rows:
            return 0
        with Repository() as repo:
            for r in rows:
                out = r.pop("outcome")
                r["last_seen_at"] = datetime.utcnow()
                m = repo.upsert_market(r)
                rule = parse_rule(out["raw_label"])
                repo.upsert_outcome(
                    m.id,
                    {
                        "raw_label": out["raw_label"],
                        "canonical_term": rule.canonical_term,
                        "threshold_type": rule.threshold_type,
                        "threshold_value": rule.threshold_value,
                        "alias_json": json.dumps(rule.aliases),
                        "yes_price": out["yes_price"],
                        "no_price": out["no_price"],
                        "implied_probability": out["implied_probability"],
                        "notes_json": json.dumps({"notes": rule.notes}),
                    },
                )
        log.info("Synced %s markets", len(rows))
        return len(rows)

    def list_outcomes(self) -> list[tuple[Market, Outcome]]:
        with Repository() as repo:
            rows = repo.session.execute(select(Market, Outcome).join(Outcome, Outcome.market_id == Market.id)).all()
            return rows
