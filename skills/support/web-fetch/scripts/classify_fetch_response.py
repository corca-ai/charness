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
JSONP_OR_ASSIGNMENT_RE = re.compile(r"^[A-Za-z_$][\w$]*(?:\.[A-Za-z_$][\w$]*)*\s*(?:=|\()\s*[\[{]")
XSSI_PREFIXES = (")]}',", ")]}'", "while(1);", "for(;;);")

LOGIN_MARKER_REGEXES = (
    ("sign in", re.compile(r"(?<!\w)sign(?:\s+|-)in(?!\w)")),
    ("log in", re.compile(r"(?<!\w)log(?:\s+|-)in(?!\w)")),
    ("login", re.compile(r"(?<!\w)login(?!\w)")),
    ("로그인", re.compile(r"(?<!\w)로그인(?!\w)")),
)
HARD_CAPTCHA_PATTERNS = (
    "captcha",
    "verify you are human",
    "cf-challenge",
)
SOFT_CAPTCHA_PATTERNS = (
    "robot",
)
ERROR_PATTERNS = (
    "access denied",
    "not found",
    "403 error",
    "403 forbidden",
    "404 not found",
    "429 too many requests",
    "request blocked",
    "request could not be satisfied",
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
BOT_CHALLENGE_PATTERNS = (
    "access denied",
    "just a moment",
    "checking your browser",
    "sec-if-cpt-container",
    "powered and protected by akamai",
    "datadome",
    "request unsuccessful. incapsula",
    "the requested url was rejected",
)
EMPTY_SHELL_PATTERNS = (
    'id="root"',
    'id="__next"',
    "app-root",
)


def extract_text(raw: str) -> str:
    unescaped = html.unescape(raw)
    without_tags = TAG_RE.sub(" ", unescaped)
    return WHITESPACE_RE.sub(" ", without_tags).strip()


def _matched_login_markers(text: str) -> list[str]:
    folded = text.casefold()
    return [label for label, pattern in LOGIN_MARKER_REGEXES if pattern.search(folded)]


def _captcha_patterns(lowered: str, text_length: int) -> tuple[str, ...]:
    if any(pattern in lowered for pattern in HARD_CAPTCHA_PATTERNS):
        return HARD_CAPTCHA_PATTERNS
    if any(pattern in lowered for pattern in SOFT_CAPTCHA_PATTERNS) and text_length < 1000:
        return SOFT_CAPTCHA_PATTERNS
    return ()


def _looks_like_json_response(raw: str) -> bool:
    stripped = raw.lstrip("\ufeff \t\r\n")
    for prefix in XSSI_PREFIXES:
        if stripped.startswith(prefix):
            stripped = stripped.removeprefix(prefix).lstrip()
            break
    if stripped.startswith("{"):
        return True
    if stripped.startswith("["):
        if len(stripped) > 1 and stripped[1] in "{[\"-0123456789tfn]":
            return True
        try:
            json.loads(stripped)
        except Exception:
            return False
        return True
    return bool(JSONP_OR_ASSIGNMENT_RE.match(stripped))


def extract_persistable_text(raw: str, *, content_format: str = "text") -> str | None:
    if content_format == "markdown":
        return raw
    if _looks_like_json_response(raw):
        return None
    return extract_text(raw)


def _json_field(raw: str, field_path: str) -> bool:
    try:
        current: object = json.loads(raw)
    except Exception:
        return False
    for part in field_path.split("."):
        if isinstance(current, dict) and part in current:
            current = current[part]
        else:
            return False
    return current not in (None, "", [], {})


def _proof_matches(
    raw: str,
    *,
    expect_text: list[str],
    expect_regex: list[str],
    expect_json_field: list[str],
) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    matches: list[dict[str, str]] = []
    errors: list[dict[str, str]] = []
    for expected in expect_text:
        if expected and expected in raw:
            matches.append({"type": "text", "value": expected})
    for pattern in expect_regex:
        try:
            if re.search(pattern, raw, flags=re.IGNORECASE | re.MULTILINE):
                matches.append({"type": "regex", "value": pattern})
        except re.error:
            errors.append({"type": "invalid-regex", "value": pattern})
    for field_path in expect_json_field:
        if _json_field(raw, field_path):
            matches.append({"type": "json-field", "value": field_path})
    return matches, errors


def _fallback_candidates(status: str, *, intent: str, proof_required: bool) -> list[str]:
    if status == "success" and not proof_required:
        return []
    if status == "success":
        return ["clean-stop"]
    if status in {"partial-content", "unclear"}:
        return ["impersonated-public-fetch", "defuddle", "patchright-render", "agent-browser-render", "archive"]
    if status == "empty-spa":
        candidates = ["patchright-render", "agent-browser-render"]
        if intent == "collect":
            candidates.extend(["patchright-network-recon", "agent-browser-network-recon"])
        candidates.extend(["defuddle", "archive"])
        return candidates
    if status in {"captcha", "error-page", "login-wall"}:
        candidates = ["impersonated-public-fetch", "patchright-render", "agent-browser-render"]
        if intent == "collect":
            candidates.extend(["patchright-network-recon", "agent-browser-network-recon"])
        candidates.append("clean-stop")
        return candidates
    return ["impersonated-public-fetch", "defuddle", "patchright-render", "agent-browser-render", "archive", "clean-stop"]


def _prepare_proof(
    raw: str,
    expect_text: list[str] | None,
    expect_regex: list[str] | None,
    expect_json_field: list[str] | None,
) -> tuple[list[dict[str, str]], list[dict[str, str]], bool]:
    expect_text = expect_text or []
    expect_regex = expect_regex or []
    expect_json_field = expect_json_field or []
    proof, proof_errors = _proof_matches(
        raw,
        expect_text=expect_text,
        expect_regex=expect_regex,
        expect_json_field=expect_json_field,
    )
    return proof, proof_errors, bool(expect_text or expect_regex or expect_json_field)


def classify(
    raw: str,
    *,
    expect_text: list[str] | None = None,
    expect_regex: list[str] | None = None,
    expect_json_field: list[str] | None = None,
    intent: str = "single",
) -> dict[str, object]:
    lowered = raw.lower()
    text = extract_text(raw)
    text_length = len(text)
    matched: list[str] = []
    signals: list[str] = []
    proof, proof_errors, proof_required = _prepare_proof(raw, expect_text, expect_regex, expect_json_field)

    if proof_errors:
        status = "invalid-proof"
        confidence = "none"
        matched.extend(f"{item['type']}:{item['value']}" for item in proof_errors)
        signals.append("invalid-proof")
        next_step = "Fix the proof input before trusting this acquisition."
    elif (captcha_patterns := _captcha_patterns(lowered, text_length)):
        matched.extend(pattern for pattern in captcha_patterns if pattern in lowered)
        status = "captcha"
        confidence = "none"
        signals.append("captcha")
        next_step = "Try the next fallback route or stop with the bot-block noted."
    elif (matched_login_markers := _matched_login_markers(text)):
        matched.extend(matched_login_markers)
        status = "login-wall"
        confidence = "none"
        signals.append("login-wall")
        next_step = "Stop cleanly unless a stronger authenticated access path exists."
    elif any(pattern in lowered for pattern in BOT_CHALLENGE_PATTERNS):
        matched.extend(pattern for pattern in BOT_CHALLENGE_PATTERNS if pattern in lowered)
        status = "captcha"
        confidence = "none"
        signals.append("bot-challenge")
        next_step = "Try read-only browser rendering or stop with the challenge recorded."
    elif any(pattern in lowered for pattern in EMPTY_SPA_PATTERNS):
        matched.extend(pattern for pattern in EMPTY_SPA_PATTERNS if pattern in lowered)
        status = "empty-spa"
        confidence = "none"
        signals.append("empty-spa")
        next_step = "Prefer a reader, browser, or domain-specific API path."
    elif any(pattern in lowered for pattern in ERROR_PATTERNS):
        matched.extend(pattern for pattern in ERROR_PATTERNS if pattern in lowered)
        status = "error-page"
        confidence = "none"
        signals.append("error-page")
        next_step = "Treat this as a failed fetch and move to the next route."
    elif proof:
        status = "success"
        confidence = "strong"
        matched.extend(f"{item['type']}:{item['value']}" for item in proof)
        signals.append("positive-proof")
        next_step = "Use the content as a source and preserve the matched proof."
    elif proof_required:
        status = "unclear"
        confidence = "none"
        signals.append("missing-positive-proof")
        next_step = "Do not trust this alone; try a stronger route or inspect manually."
    elif text_length >= 1000:
        status = "success"
        confidence = "weak"
        signals.append("long-text")
        next_step = "Use the content as a source and preserve the retrieval method."
    elif any(pattern in lowered for pattern in PARTIAL_PATTERNS):
        matched.extend(pattern for pattern in PARTIAL_PATTERNS if pattern in lowered)
        status = "partial-content"
        confidence = "weak"
        signals.append("metadata-only")
        next_step = "Keep only as metadata or a partial source and try a stronger route."
    elif any(pattern in lowered for pattern in EMPTY_SHELL_PATTERNS):
        matched.extend(pattern for pattern in EMPTY_SHELL_PATTERNS if pattern in lowered)
        status = "empty-spa"
        confidence = "none"
        signals.append("empty-shell-marker")
        next_step = "Use browser rendering before trusting this page."
    else:
        status = "unclear"
        confidence = "none"
        next_step = "Do not trust this alone; inspect manually or try the next route."

    return {
        "status": status,
        "confidence": confidence,
        "text_length": text_length,
        "matched_signals": matched,
        "signals": signals,
        "proof": proof,
        "proof_errors": proof_errors,
        "fallback_candidates": _fallback_candidates(status, intent=intent, proof_required=proof_required),
        "recommended_next_step": next_step,
    }


def load_input(path: str | None) -> str:
    if path:
        return Path(path).read_text(encoding="utf-8")
    return sys.stdin.read()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", help="Read the response body from this file; otherwise read stdin.")
    parser.add_argument("--expect-text", action="append", default=[], help="Require literal text as positive proof (repeatable).")
    parser.add_argument("--expect-regex", action="append", default=[], help="Require a regex match as positive proof (repeatable).")
    parser.add_argument("--expect-json-field", action="append", default=[], help="Require a non-empty JSON field path as proof (repeatable).")
    parser.add_argument("--intent", choices=("single", "collect"), default="single", help="Classification intent: one source or a collection.")
    args = parser.parse_args()
    raw = load_input(args.path)
    # Imported here, not at module scope: this file is also imported as a library
    # by siblings that put the package directory on `sys.path` themselves, and
    # only the CLI entry (whose own directory is on `sys.path`) needs a renderer.
    from route_public_fetch import load_yaml_output

    load_yaml_output().emit_yaml(
        classify(
            raw,
            expect_text=args.expect_text,
            expect_regex=args.expect_regex,
            expect_json_field=args.expect_json_field,
            intent=args.intent,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
