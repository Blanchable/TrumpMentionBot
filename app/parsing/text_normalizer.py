from __future__ import annotations

import re


def normalize_text(text: str) -> tuple[str, str]:
    cleaned = text.replace("’", "'").replace("“", '"').replace("”", '"')
    cleaned = re.sub(r"\[[^\]]+\]", " ", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    normalized = cleaned.lower()
    return cleaned, normalized
