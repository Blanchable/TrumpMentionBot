from __future__ import annotations

import json

from sqlalchemy import select

from app.db.models import Outcome, Transcript
from app.db.repository import Repository
from app.parsing.matcher import run_match
from app.parsing.rule_parser import parse_rule


class MatcherService:
    def run_all(self) -> int:
        count = 0
        with Repository() as repo:
            outcomes = list(repo.session.scalars(select(Outcome)))
            transcripts = list(repo.session.scalars(select(Transcript).where(Transcript.fetch_status == "ok")))
            for t in transcripts:
                for o in outcomes:
                    rule = parse_rule(o.raw_label)
                    res = run_match(rule, t.normalized_text)
                    repo.replace_match(
                        t.id,
                        o.id,
                        {
                            "raw_count": res.raw_count,
                            "adjusted_count": res.adjusted_count,
                            "matched_spans_json": json.dumps(res.matched_spans),
                            "ambiguous_spans_json": json.dumps(res.ambiguous_spans),
                            "notes_json": json.dumps({"confidence": res.confidence_notes}),
                        },
                    )
                    count += 1
        return count
