from __future__ import annotations

import re
from dataclasses import dataclass

from app.parsing.rule_parser import RuleObject


@dataclass
class MatchResult:
    raw_count: int
    adjusted_count: int
    matched_spans: list[dict]
    ambiguous_spans: list[dict]
    confidence_notes: str


def run_match(rule: RuleObject, normalized_text: str, context_chars: int = 32) -> MatchResult:
    pattern = re.compile(rule.regex_pattern, re.IGNORECASE)
    spans = []
    for m in pattern.finditer(normalized_text):
        start, end = m.span()
        spans.append(
            {
                "term": m.group(0),
                "start": start,
                "end": end,
                "context": normalized_text[max(0, start - context_chars) : min(len(normalized_text), end + context_chars)],
            }
        )
    raw = len(spans)
    adjusted = raw
    ambiguous = []
    if raw > 0 and len(rule.canonical_term) <= 3:
        adjusted = max(0, raw - 1)
        ambiguous = spans[:1]
    return MatchResult(raw, adjusted, spans, ambiguous, f"threshold={rule.threshold_value}")
