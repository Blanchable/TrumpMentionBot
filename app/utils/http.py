from __future__ import annotations

import httpx


def build_client(timeout_seconds: int, user_agent: str = "TrumpMentionsEngine/1.0") -> httpx.Client:
    return httpx.Client(timeout=timeout_seconds, headers={"User-Agent": user_agent}, follow_redirects=True)
