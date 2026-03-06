from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class RuleObject:
    canonical_term: str
    raw_term_label: str
    threshold_type: str
    threshold_value: int
    aliases: list[str]
    plural_forms: list[str]
    possessive_forms: list[str]
    regex_pattern: str
    notes: str


def parse_rule(raw_label: str) -> RuleObject:
    label = raw_label.strip()
    threshold_match = re.search(r"(\d+)\+", label)
    threshold = int(threshold_match.group(1)) if threshold_match else 1
    threshold_type = "at_least" if threshold > 1 else "single"

    term = re.sub(r"\d+\+", "", label).strip(" -:()[]")
    term = re.sub(r"\s+", " ", term)
    canonical = term.lower()
    aliases = list({canonical, canonical.replace("-", " ")})
    plurals = [f"{canonical}s"] if not canonical.endswith("s") else [canonical]
    possessives = [f"{canonical}'s", f"{canonical}s'"]
    regex = rf"\b({re.escape(canonical)}|{re.escape(canonical.replace('-', ' '))})\b"
    notes = "Auto-parsed from outcome label"
    return RuleObject(canonical, raw_label, threshold_type, threshold, aliases, plurals, possessives, regex, notes)
