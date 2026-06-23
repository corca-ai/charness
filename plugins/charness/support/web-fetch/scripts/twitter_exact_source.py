#!/usr/bin/env python3
"""Exact-source acquisition for X/Twitter status URLs (the `domain-specific-route`
stage of the `twitter-syndication` route).

A raw `x.com`/`twitter.com` status page is usually captcha/bot-blocked. This stage
fetches the EXACT post through identity-keyed public endpoints (the syndication
CDN keyed on the status id, then oEmbed), and only treats a result as the original
when the returned status id MATCHES the requested one. A mismatch is recorded as
`invalid-proof` and never substituted; an all-blocked outcome is recorded honestly
so the agent can stop with "exact source unavailable" rather than passing off a
merely-similar public source as the original.

Live fetching is injected (a fetcher callable), so the default is non-live: tests
and host grants seed responses; an operator opts into live fetch explicitly.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Callable
from urllib.parse import quote, urlparse

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from acquisition_trace_lib import AcquisitionAttempt, skip_attempt  # noqa: E402
from classify_fetch_response import classify  # noqa: E402
from source_identity_lib import attempt_endpoint, has_outcome, stage_attempts  # noqa: E402

STAGE_ID = "domain-specific-route"
X_HOSTS = {"x.com", "twitter.com", "mobile.x.com", "mobile.twitter.com"}
STATUS_PATH_RE = re.compile(r"^/(?P<handle>[A-Za-z0-9_]{1,15})/status(?:es)?/(?P<id>\d+)")
STATUS_ID_IN_URL_RE = re.compile(r"/status(?:es)?/(\d+)")
BLOCKED_STATUSES = {"captcha", "login-wall", "error-page"}

# A fetcher maps an endpoint dict to (text, error); either may be None.
Fetcher = Callable[[dict], "tuple[str | None, str | None]"]


def parse_status_url(url: str) -> dict | None:
    """Return {handle, status_id} for an X/Twitter status URL, else None."""
    parsed = urlparse(url)
    host = (parsed.netloc or "").lower()
    if host.startswith("www."):
        host = host[4:]
    if host not in X_HOSTS:
        return None
    match = STATUS_PATH_RE.match(parsed.path)
    if match is None:
        return None
    return {"handle": match.group("handle"), "status_id": match.group("id")}


def build_endpoints(parsed: dict) -> list[dict]:
    """Ordered identity-keyed exact-source endpoints for one status post."""
    status_id = parsed["status_id"]
    canonical = f"https://x.com/{parsed['handle']}/status/{status_id}"
    return [
        {
            "kind": "syndication",
            "tool_id": "twitter-syndication",
            "url": f"https://cdn.syndication.twimg.com/tweet-result?id={status_id}&lang=en",
        },
        {
            "kind": "oembed",
            "tool_id": "twitter-oembed",
            "url": f"https://publish.twitter.com/oembed?url={quote(canonical, safe='')}&omit_script=1",
        },
    ]


def returned_status_id(kind: str, text: str) -> str | None:
    """Extract the status id the endpoint response actually identifies."""
    try:
        data = json.loads(text)
    except (json.JSONDecodeError, TypeError):
        data = None
    if isinstance(data, dict):
        if kind == "syndication":
            for key in ("id_str", "id"):
                value = data.get(key)
                if value not in (None, ""):
                    return str(value)
        elif kind == "oembed":
            # oEmbed echoes back the URL we passed, so a matching id only proves
            # "this is the id I asked for", not that the post exists. Require a
            # rendered body (html/author_name) so a bare 200 echo for a deleted or
            # nonexistent post is not accepted as the original; return terminally
            # so the raw-text fallback cannot reintroduce the echoed id.
            if data.get("html") or data.get("author_name"):
                for key in ("url", "author_url", "html"):
                    value = data.get(key)
                    if isinstance(value, str):
                        match = STATUS_ID_IN_URL_RE.search(value)
                        if match is not None:
                            return match.group(1)
            return None
    match = STATUS_ID_IN_URL_RE.search(text or "")
    return match.group(1) if match is not None else None


def _endpoint_attempt(requested_id: str, endpoint: dict, text: str | None, error: str | None) -> AcquisitionAttempt:
    base = {"endpoint": endpoint["url"], "kind": endpoint["kind"], "requested_status_id": requested_id}
    tool_id = endpoint["tool_id"]
    if error or not (text or "").strip():
        reason = "fetch-failed" if error else "empty-response"
        return AcquisitionAttempt(STAGE_ID, tool_id, status="error", error=error or "empty-response", details={**base, "reason": reason})
    classification = classify(text)
    if classification["status"] in BLOCKED_STATUSES:
        return AcquisitionAttempt(STAGE_ID, tool_id, status=str(classification["status"]), classification=classification, details={**base, "reason": "blocked"})
    returned = returned_status_id(endpoint["kind"], text)
    if returned is None:
        return AcquisitionAttempt(STAGE_ID, tool_id, status="error", details={**base, "reason": "no-identity"})
    identity = {"requested_status_id": requested_id, "returned_status_id": returned, "matched": returned == requested_id, "verified_via": endpoint["kind"]}
    if returned == requested_id:
        return AcquisitionAttempt(STAGE_ID, tool_id, status="success", confidence="strong", content_text=text, content_format="json", details={**base, "identity_proof": identity, "outcome": "exact-fetched"})
    return AcquisitionAttempt(STAGE_ID, tool_id, status="invalid-proof", details={**base, "identity_proof": identity, "reason": "identity-mismatch", "outcome": "identity-rejected"})


def run_exact_source_stage(url: str, *, fetcher: Fetcher) -> list[AcquisitionAttempt]:
    """Try each exact-source endpoint until one proves the exact post identity.

    Returns one attempt per endpoint tried (failed/blocked attempts stay visible in
    the trace). A non-status URL yields a single honest skip; the by-id exact route
    cannot prove identity for a profile/timeline URL."""
    parsed = parse_status_url(url)
    if parsed is None:
        return [skip_attempt(STAGE_ID, None, reason="no-status-id")]
    attempts: list[AcquisitionAttempt] = []
    for endpoint in build_endpoints(parsed):
        text, error = fetcher(endpoint)
        attempt = _endpoint_attempt(parsed["status_id"], endpoint, text, error)
        attempts.append(attempt)
        if attempt.status == "success":
            break
    return attempts


def classify_source_identity(acquisition: dict) -> str:
    """Answer-path source-identity verdict over an acquisition trace.

    `exact-fetched` — the exact post was retrieved with a matching status id.
    `exact-blocked` — the exact route was attempted but blocked / returned a
    mismatched or empty response (the agent must stop or explicitly label any
    fallback as a *similar* source, never as the original).
    `exact-unavailable` — the exact route did not run (live fetch off / no status
    id), so no exact source exists yet.
    `not-applicable` — not an X/Twitter exact-source route.
    Gather never emits `similar-source`: substituting a similar source as the
    original is the wrong outcome this contract exists to prevent."""
    route = acquisition.get("route")
    if not isinstance(route, dict) or route.get("route_id") != "twitter-syndication":
        return "not-applicable"
    domain = stage_attempts(acquisition, STAGE_ID)
    if has_outcome(domain, "exact-fetched"):
        return "exact-fetched"
    # An attempt that actually fetched an endpoint carries `details.endpoint` and
    # is not the live-fetch-off stub; a no-status-id stub carries no endpoint.
    executed = [a for a in domain if attempt_endpoint(a) and a.get("error") != "live-fetch-not-enabled"]
    return "exact-blocked" if executed else "exact-unavailable"


def make_fetcher(seed_map: dict | None = None, *, live: bool = False, live_fetch: Callable[[str], "tuple[str | None, str | None]"] | None = None) -> Fetcher:
    """Build a fetcher. Seeded responses win (tests / host grants); live network
    fetch runs only when explicitly enabled; otherwise the endpoint is recorded as
    not retrieved so gather stops honestly instead of substituting."""

    def fetch(endpoint: dict) -> "tuple[str | None, str | None]":
        endpoint_url = endpoint["url"]
        if seed_map and endpoint_url in seed_map:
            entry = seed_map[endpoint_url]
            return entry.get("text"), entry.get("error")
        if live and live_fetch is not None:
            return live_fetch(endpoint_url)
        return None, "live-fetch-not-enabled"

    return fetch
