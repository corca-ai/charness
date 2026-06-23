"""Small URL reader shared by public URL acquisition helpers."""

from __future__ import annotations

import urllib.request


def read_url(url: str, *, timeout: int, headers: dict[str, str] | None = None) -> tuple[str, str | None]:
    request = urllib.request.Request(url, headers=headers or {})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            charset = response.headers.get_content_charset() or "utf-8"
            return response.read().decode(charset, errors="replace"), None
    except Exception as exc:
        return "", f"{type(exc).__name__}:{str(exc)[:200]}"
