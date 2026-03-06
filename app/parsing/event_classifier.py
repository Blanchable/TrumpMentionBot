from __future__ import annotations


def classify_event(title: str) -> str:
    t = title.lower()
    if "press" in t:
        return "press"
    if "rally" in t:
        return "rally"
    if "interview" in t:
        return "interview"
    return "speech"
