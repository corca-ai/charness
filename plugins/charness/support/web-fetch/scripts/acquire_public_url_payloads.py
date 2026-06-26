from __future__ import annotations

import argparse

import reddit_source
import twitter_exact_source
import youtube_source
from acquisition_trace_lib import AcquisitionAttempt, payload


def payload_for(
    args: argparse.Namespace,
    route: dict[str, object],
    attempts: list[AcquisitionAttempt],
    disposition: str,
) -> dict[str, object]:
    result = payload(
        args.url,
        route,
        attempts,
        disposition,
        intent=args.intent,
        include_selected_content=args.include_selected_content,
        selected_content_max_chars=args.selected_content_max_chars,
    )
    if route.get("route_id") == "twitter-syndication":
        result["source_identity"] = twitter_exact_source.classify_source_identity(result)
        result["source_resolution"] = twitter_exact_source.classify_source_resolution(result)
    if route.get("route_id") == "reddit-feed":
        result["source_identity"] = reddit_source.classify_source_identity(result)
    if route.get("route_id") == "yt-dlp-metadata":
        result["source_identity"] = youtube_source.classify_source_identity(result)
    return result


def invalid_scheme_payload(args: argparse.Namespace, parsed) -> dict[str, object]:
    route = {
        "input_url": args.url,
        "normalized_host": parsed.netloc or parsed.path,
        "route_id": "invalid-url-scheme",
        "route_family": "invalid-input",
        "summary": "Only http and https public URLs are supported.",
        "required_tools": [],
        "access_modes": [],
        "fallback_order": [],
        "acquisition_plan": [],
        "notes": ["Rejected before any acquisition tool was invoked."],
    }
    attempts = [
        AcquisitionAttempt(
            stage_id="input-validation",
            tool_id=None,
            status="error",
            error=f"unsupported-url-scheme:{parsed.scheme or 'missing'}",
            details={"allowed_schemes": ["http", "https"]},
        )
    ]
    return payload_for(args, route, attempts, "error")
