from __future__ import annotations

import importlib.util
from dataclasses import dataclass
from pathlib import Path
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
    "reddit-feed": Route(
        route_id="reddit-feed",
        route_family="public-api",
        summary="Prefer Reddit RSS feeds, with JSON as a secondary source-bound public route.",
        required_tools=(),
        access_modes=("public", "degraded"),
        notes=(
            "Add `.rss` endpoints for posts and subreddit listings before `.json`.",
            "Unauthenticated JSON can be WAF-sensitive; RSS is usually the cheaper public route.",
        ),
    ),
    "hacker-news-firebase": Route(
        route_id="hacker-news-firebase",
        route_family="public-api",
        summary="Prefer the Hacker News Firebase API over raw HTML.",
        required_tools=("curl",),
        access_modes=("public",),
        notes=("Use story and item ids from the Firebase API for structured data.",),
    ),
    "stackexchange-api": Route(
        route_id="stackexchange-api",
        route_family="public-api",
        summary="Prefer the Stack Exchange API instead of blocked raw HTML fetch.",
        required_tools=("curl",),
        access_modes=("public", "degraded"),
        notes=("Use API filters that include bodies only when the response needs them.",),
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
    "github-host-mediated": Route(
        route_id="github-host-mediated",
        route_family="host-mediated",
        summary="Use the host's github capability command; do not invoke direct `gh` under adapter mode `host-mediated`.",
        required_tools=(),
        access_modes=("grant", "public", "degraded"),
        notes=(
            "Adapter declared gather_provider.github.mode=host-mediated.",
            "Follow the host's documented github capability shape; never substitute direct `gh`.",
        ),
    ),
    "github-missing-capability": Route(
        route_id="github-missing-capability",
        route_family="public-only",
        summary="Adapter declared gather_provider.github.mode=none; stop with missing-capability or use public REST only.",
        required_tools=(),
        access_modes=("public", "degraded"),
        notes=(
            "Adapter declared gather_provider.github.mode=none.",
            "Do not invoke `gh` or a host capability; only world-readable public REST is allowed.",
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
        notes=("Convert desktop blog URLs into the `m.blog.naver.com/PostView.naver` form when possible.",),
    ),
    "reader-fallback": Route(
        route_id="reader-fallback",
        route_family="public-reader",
        summary="Prefer a reader-style fallback after direct fetch fails or returns weak HTML.",
        required_tools=("curl",),
        access_modes=("public", "degraded"),
        notes=("Use this for JS-heavy or iframe-heavy public pages when a domain-specific API is not stronger.",),
    ),
    "direct-then-fallback": Route(
        route_id="direct-then-fallback",
        route_family="public",
        summary="Try direct public fetch first, then reader, metadata-only, and archive fallback in order.",
        required_tools=("curl",),
        access_modes=("grant", "public", "degraded"),
        notes=("Do not skip the direct path when the page may still be readable as plain HTML.",),
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

GITHUB_ROUTE_FOR_MODE = {
    "direct-cli": "github-grant-or-cli",
    "host-mediated": "github-host-mediated",
    "none": "github-missing-capability",
}


def normalized_host(url: str) -> str:
    parsed = urlparse(url)
    host = (parsed.netloc or parsed.path).strip().lower()
    if host.startswith("www."):
        host = host[4:]
    return host.split(":", 1)[0]


def host_matches(host: str, patterns: Sequence[str]) -> bool:
    return any(host == pattern or host.endswith(f".{pattern}") for pattern in patterns)


def _find_gather_adapter_script() -> Path:
    script = Path(__file__).resolve()
    for ancestor in script.parents:
        for candidate in (
            ancestor / "skills" / "public" / "gather" / "scripts" / "resolve_adapter.py",
            ancestor / "skills" / "gather" / "scripts" / "resolve_adapter.py",
        ):
            if candidate.is_file():
                return candidate
    return Path("__missing_gather_resolve_adapter__.py")


def resolve_github_mode(repo_root: Path | None) -> str:
    if repo_root is None:
        return "direct-cli"
    adapter_script = _find_gather_adapter_script()
    if not adapter_script.is_file():
        return "direct-cli"
    spec = importlib.util.spec_from_file_location("web_fetch_gather_adapter", adapter_script)
    if spec is None or spec.loader is None:
        return "direct-cli"
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
        payload = module.load_adapter(repo_root)
    except Exception:
        return "direct-cli"
    provider = payload.get("data", {}).get("gather_provider") or {}
    entry = provider.get("github") or {}
    mode = entry.get("mode", "direct-cli")
    return mode if mode in GITHUB_ROUTE_FOR_MODE else "direct-cli"


def route_id_for_host(host: str, *, github_mode: str) -> str:
    if host_matches(host, ("x.com", "twitter.com")):
        return "twitter-syndication"
    if host_matches(host, ("reddit.com",)):
        return "reddit-feed"
    if host_matches(host, ("news.ycombinator.com",)):
        return "hacker-news-firebase"
    if host_matches(host, ("stackoverflow.com", "stackexchange.com")):
        return "stackexchange-api"
    if host_matches(host, ("github.com",)):
        return GITHUB_ROUTE_FOR_MODE[github_mode]
    if host_matches(host, tuple(MEDIA_DOMAINS)):
        return "yt-dlp-metadata"
    if host_matches(host, ("blog.naver.com",)):
        return "naver-blog-mobile"
    if host_matches(host, tuple(READER_DOMAINS)) or host.endswith(".substack.com"):
        return "reader-fallback"
    return "direct-then-fallback"
