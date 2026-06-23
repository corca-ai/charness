#!/usr/bin/env python3
"""Public Reddit source acquisition for the web-fetch domain route.

Reddit's raw HTML and unauthenticated JSON endpoint can be WAF-sensitive. The
public feed endpoint remains the cheapest source-bound route for posts and
subreddit listings, so try RSS first and keep JSON as a secondary route.
"""
from __future__ import annotations

import json
from urllib.parse import urlparse

from acquisition_trace_lib import AcquisitionAttempt, skip_attempt
from classify_fetch_response import classify, extract_persistable_text
from source_identity_lib import attempt_endpoint, direct_page_success, has_outcome, stage_attempts

STAGE_ID = "domain-specific-route"
REDDIT_HOSTS = ("reddit.com", ".reddit.com")
ENDPOINT_SUFFIXES = {
    True: ((".rss", "rss", "reddit-rss"), (".json", "json", "reddit-json")),
    False: (("/.rss", "rss", "reddit-rss"), ("/.json", "json", "reddit-json")),
}
SUCCESS_FORMAT = {
    "rss": ("xml", "feed-fetched"),
    "json": ("json", "json-fetched"),
}


def _normalized_url(url: str) -> str:
    parsed = urlparse(url)
    if not parsed.scheme or not parsed.netloc:
        return url
    path = parsed.path or "/"
    return f"{parsed.scheme}://{parsed.netloc}{path}".rstrip("/")


def _endpoints(url: str) -> list[dict[str, str]]:
    base = _normalized_url(url)
    host = (urlparse(base).netloc or "").lower()
    if host.startswith("www."):
        host = host[4:]
    if host != REDDIT_HOSTS[0] and not host.endswith(REDDIT_HOSTS[1]):
        return []
    return [
        {"kind": kind, "tool_id": tool_id, "url": base + suffix}
        for suffix, kind, tool_id in ENDPOINT_SUFFIXES["/comments/" in urlparse(base).path]
    ]


def _looks_like_feed(text: str) -> bool:
    sample = text.lstrip().lower()
    return sample.startswith(("<?xml", "<rss", "<feed")) or "<rss" in sample[:500] or "<feed" in sample[:500]


def _looks_like_json(text: str) -> bool:
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        return False
    return payload not in ({}, [], None, "")


def _proof_required(expect_text: list[str], expect_regex: list[str], expect_json_field: list[str]) -> bool:
    return bool(expect_text or expect_regex or expect_json_field)


def _success_details(endpoint: dict[str, str], body: str) -> tuple[str, str] | None:
    if endpoint["kind"] == "rss" and _looks_like_feed(body):
        return SUCCESS_FORMAT["rss"]
    if endpoint["kind"] == "json" and _looks_like_json(body):
        return SUCCESS_FORMAT["json"]
    return None


def _success_attempt(
    endpoint: dict[str, str],
    body: str,
    classification: dict,
    content_format: str,
    outcome: str,
) -> AcquisitionAttempt:
    return AcquisitionAttempt(
        STAGE_ID,
        endpoint["tool_id"],
        status="success",
        confidence="strong",
        output_chars=len(body),
        classification=classification,
        details={"endpoint": endpoint["url"], "kind": endpoint["kind"], "outcome": outcome},
        content_text=extract_persistable_text(body, content_format=content_format),
        content_format=content_format,
    )


def _attempt(
    endpoint: dict[str, str],
    text: str | None,
    error: str | None,
    *,
    expect_text: list[str],
    expect_regex: list[str],
    expect_json_field: list[str],
    intent: str,
) -> AcquisitionAttempt:
    details = {"endpoint": endpoint["url"], "kind": endpoint["kind"]}
    if error or not (text or "").strip():
        return AcquisitionAttempt(
            STAGE_ID,
            endpoint["tool_id"],
            status="error",
            error=error or "empty-response",
            details={**details, "reason": "fetch-failed" if error else "empty-response"},
        )
    body = text or ""
    classification = classify(
        body,
        expect_text=expect_text,
        expect_regex=expect_regex,
        expect_json_field=expect_json_field,
        intent=intent,
    )
    if _proof_required(expect_text, expect_regex, expect_json_field) and classification["status"] != "success":
        return AcquisitionAttempt(
            STAGE_ID,
            endpoint["tool_id"],
            status=str(classification["status"]),
            confidence=str(classification.get("confidence", "none")),
            output_chars=len(body),
            classification=classification,
            details={**details, "reason": "missing-positive-proof"},
        )
    success = _success_details(endpoint, body)
    if success is not None:
        return _success_attempt(endpoint, body, classification, *success)
    return AcquisitionAttempt(
        STAGE_ID,
        endpoint["tool_id"],
        status="error",
        output_chars=len(body),
        details={**details, "reason": "no-feed-or-json"},
    )


def run_reddit_stage(
    url: str,
    *,
    fetcher,
    expect_text: list[str] | None = None,
    expect_regex: list[str] | None = None,
    expect_json_field: list[str] | None = None,
    intent: str = "single",
) -> list[AcquisitionAttempt]:
    endpoints = _endpoints(url)
    if not endpoints:
        return [skip_attempt(STAGE_ID, None, reason="not-reddit-url")]
    attempts: list[AcquisitionAttempt] = []
    text_expectations = expect_text or []
    regex_expectations = expect_regex or []
    json_expectations = expect_json_field or []
    for endpoint in endpoints:
        text, error = fetcher(endpoint)
        attempt = _attempt(
            endpoint,
            text,
            error,
            expect_text=text_expectations,
            expect_regex=regex_expectations,
            expect_json_field=json_expectations,
            intent=intent,
        )
        attempts.append(attempt)
        if attempt.status == "success":
            break
    return attempts


def classify_source_identity(acquisition: dict) -> str:
    route = acquisition.get("route")
    if not isinstance(route, dict) or route.get("route_id") != "reddit-feed":
        return "not-applicable"
    domain = stage_attempts(acquisition, STAGE_ID)
    if has_outcome(domain, "feed-fetched"):
        return "feed-fetched"
    if has_outcome(domain, "json-fetched"):
        return "json-fetched"
    if direct_page_success(acquisition):
        return "direct-page-fetched"
    if any(attempt_endpoint(a) for a in domain):
        return "feed-blocked"
    return "feed-unavailable"
