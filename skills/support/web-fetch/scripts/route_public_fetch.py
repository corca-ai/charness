#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from typing import Sequence
from urllib.parse import urlparse


@dataclass(frozen=True)
class Route:
    route_id: str
    route_family: str
    summary: str
    required_tools: tuple[str, ...]
    access_modes: tuple[str, ...]
    notes: tuple[str, ...]


ROUTES: dict[str, Route] = {
    "twitter-syndication": Route(
        route_id="twitter-syndication",
        route_family="public-api",
        summary="Use search for discovery, then prefer Syndication API or oEmbed over raw page fetch.",
        required_tools=(),
        access_modes=("grant", "public", "degraded"),
        notes=(
            "Raw fetch is often blocked or incomplete.",
            "Syndication helps for timelines; oEmbed helps when the exact post URL is known.",
        ),
    ),
    "reddit-json": Route(
        route_id="reddit-json",
        route_family="public-api",
        summary="Prefer Reddit JSON endpoints with a mobile user agent.",
        required_tools=("curl",),
        access_modes=("public", "degraded"),
        notes=(
            "Add `.json` endpoints for posts and subreddit listings.",
            "A mobile user agent improves public access reliability.",
        ),
    ),
    "hacker-news-firebase": Route(
        route_id="hacker-news-firebase",
        route_family="public-api",
        summary="Prefer the Hacker News Firebase API over raw HTML.",
        required_tools=("curl",),
        access_modes=("public",),
        notes=(
            "Use story and item ids from the Firebase API for structured data.",
        ),
    ),
    "stackexchange-api": Route(
        route_id="stackexchange-api",
        route_family="public-api",
        summary="Prefer the Stack Exchange API instead of blocked raw HTML fetch.",
        required_tools=("curl",),
        access_modes=("public", "degraded"),
        notes=(
            "Use API filters that include bodies only when the response needs them.",
        ),
    ),
    "github-grant-or-cli": Route(
        route_id="github-grant-or-cli",
        route_family="authenticated-binary",
        summary="Prefer runtime grant or authenticated `gh`; fall back to public GitHub REST only when scope stays public.",
        required_tools=("gh",),
        access_modes=("grant", "binary", "public", "degraded"),
        notes=(
            "Keep private access on the grant or authenticated `gh` path.",
            "Public REST remains a fallback for world-readable metadata.",
        ),
    ),
    "yt-dlp-metadata": Route(
        route_id="yt-dlp-metadata",
        route_family="binary",
        summary="Prefer `yt-dlp` metadata, subtitle, or playlist paths for media sites.",
        required_tools=("yt-dlp",),
        access_modes=("binary", "public", "degraded"),
        notes=(
            "Use metadata-only paths before any download path.",
            "Subtitle or comment extraction remains route-specific and may fail per site.",
        ),
    ),
    "naver-blog-mobile": Route(
        route_id="naver-blog-mobile",
        route_family="public-transform",
        summary="Prefer the mobile Naver blog URL plus a mobile user agent.",
        required_tools=("curl",),
        access_modes=("public", "degraded"),
        notes=(
            "Convert desktop blog URLs into the `m.blog.naver.com/PostView.naver` form when possible.",
        ),
    ),
    "reader-fallback": Route(
        route_id="reader-fallback",
        route_family="public-reader",
        summary="Prefer a reader-style fallback after direct fetch fails or returns weak HTML.",
        required_tools=("curl",),
        access_modes=("public", "degraded"),
        notes=(
            "Use this for JS-heavy or iframe-heavy public pages when a domain-specific API is not stronger.",
        ),
    ),
    "direct-then-fallback": Route(
        route_id="direct-then-fallback",
        route_family="public",
        summary="Try direct public fetch first, then reader, metadata-only, and archive fallback in order.",
        required_tools=("curl",),
        access_modes=("grant", "public", "degraded"),
        notes=(
            "Do not skip the direct path when the page may still be readable as plain HTML.",
        ),
    ),
}

READER_DOMAINS = {
    "news.naver.com",
    "n.news.naver.com",
    "finance.naver.com",
    "clien.net",
    "ruliweb.com",
    "ppomppu.co.kr",
    "news.hada.io",
    "44bits.io",
    "careerly.co.kr",
    "brunch.co.kr",
    "medium.com",
    "news.daum.net",
}

MEDIA_DOMAINS = {
    "youtube.com",
    "youtu.be",
    "vimeo.com",
    "twitch.tv",
    "tiktok.com",
    "soundcloud.com",
}

FALLBACK_ORDER = (
    "direct-public-fetch",
    "domain-specific-route",
    "reader-or-metadata-fallback",
    "archive-or-cache",
    "clean-stop",
)


def normalized_host(url: str) -> str:
    parsed = urlparse(url)
    host = (parsed.netloc or parsed.path).strip().lower()
    if host.startswith("www."):
        host = host[4:]
    return host.split(":", 1)[0]


def host_matches(host: str, patterns: Sequence[str]) -> bool:
    return any(host == pattern or host.endswith(f".{pattern}") for pattern in patterns)


def route_for_url(url: str) -> dict[str, object]:
    host = normalized_host(url)
    if host_matches(host, ("x.com", "twitter.com")):
        route = ROUTES["twitter-syndication"]
    elif host_matches(host, ("reddit.com",)):
        route = ROUTES["reddit-json"]
    elif host_matches(host, ("news.ycombinator.com",)):
        route = ROUTES["hacker-news-firebase"]
    elif host_matches(host, ("stackoverflow.com", "stackexchange.com")):
        route = ROUTES["stackexchange-api"]
    elif host_matches(host, ("github.com",)):
        route = ROUTES["github-grant-or-cli"]
    elif host_matches(host, tuple(MEDIA_DOMAINS)):
        route = ROUTES["yt-dlp-metadata"]
    elif host_matches(host, ("blog.naver.com",)):
        route = ROUTES["naver-blog-mobile"]
    elif host_matches(host, tuple(READER_DOMAINS)) or host.endswith(".substack.com"):
        route = ROUTES["reader-fallback"]
    else:
        route = ROUTES["direct-then-fallback"]

    return {
        "input_url": url,
        "normalized_host": host,
        "route_id": route.route_id,
        "route_family": route.route_family,
        "summary": route.summary,
        "required_tools": list(route.required_tools),
        "access_modes": list(route.access_modes),
        "fallback_order": list(FALLBACK_ORDER),
        "notes": list(route.notes),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True)
    args = parser.parse_args()
    print(json.dumps(route_for_url(args.url), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
