#!/usr/bin/env python3

from __future__ import annotations

import argparse
import html
import json
import re
import sys
from pathlib import Path

TAG_RE = re.compile(r"<[^>]+>")
WHITESPACE_RE = re.compile(r"\s+")

LOGIN_PATTERNS = (
    "sign in",
    "log in",
    "login",
    "로그인",
)
CAPTCHA_PATTERNS = (
    "captcha",
    "verify you are human",
    "robot",
    "cf-challenge",
)
ERROR_PATTERNS = (
    "access denied",
    "not found",
    "403 forbidden",
    "404 not found",
    "429 too many requests",
    "temporarily unavailable",
)
EMPTY_SPA_PATTERNS = (
    '<div id="root"></div>',
    '<div id="__next"></div>',
    '<app-root></app-root>',
    "enable javascript to run this app",
)
PARTIAL_PATTERNS = (
    'property="og:title"',
    'property="og:description"',
    'name="description"',
)


def extract_text(raw: str) -> str:
    unescaped = html.unescape(raw)
    without_tags = TAG_RE.sub(" ", unescaped)
    return WHITESPACE_RE.sub(" ", without_tags).strip()


def classify(raw: str) -> dict[str, object]:
    lowered = raw.lower()
    text = extract_text(raw)
    text_length = len(text)
    matched: list[str] = []

    if any(pattern in lowered for pattern in CAPTCHA_PATTERNS):
        matched.extend(pattern for pattern in CAPTCHA_PATTERNS if pattern in lowered)
        status = "captcha"
        next_step = "Try the next fallback route or stop with the bot-block noted."
    elif any(pattern in lowered for pattern in LOGIN_PATTERNS):
        matched.extend(pattern for pattern in LOGIN_PATTERNS if pattern in lowered)
        status = "login-wall"
        next_step = "Stop cleanly unless a stronger authenticated access path exists."
    elif any(pattern in lowered for pattern in EMPTY_SPA_PATTERNS):
        matched.extend(pattern for pattern in EMPTY_SPA_PATTERNS if pattern in lowered)
        status = "empty-spa"
        next_step = "Prefer a reader, browser, or domain-specific API path."
    elif any(pattern in lowered for pattern in ERROR_PATTERNS):
        matched.extend(pattern for pattern in ERROR_PATTERNS if pattern in lowered)
        status = "error-page"
        next_step = "Treat this as a failed fetch and move to the next route."
    elif text_length >= 1000:
        status = "success"
        next_step = "Use the content as a source and preserve the retrieval method."
    elif any(pattern in lowered for pattern in PARTIAL_PATTERNS):
        matched.extend(pattern for pattern in PARTIAL_PATTERNS if pattern in lowered)
        status = "partial-content"
        next_step = "Keep only as metadata or a partial source and try a stronger route."
    else:
        status = "unclear"
        next_step = "Do not trust this alone; inspect manually or try the next route."

    return {
        "status": status,
        "text_length": text_length,
        "matched_signals": matched,
        "recommended_next_step": next_step,
    }


def load_input(path: str | None) -> str:
    if path:
        return Path(path).read_text(encoding="utf-8")
    return sys.stdin.read()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--path")
    args = parser.parse_args()
    raw = load_input(args.path)
    print(json.dumps(classify(raw), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
