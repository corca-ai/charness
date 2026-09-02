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


def _find_repo_script(*candidates: tuple[str, ...], missing: str) -> Path:
    """Ancestor-walk for a repo-owned script.

    This module has no skill-runtime bootstrap -- it is support, not a skill -- so it
    reaches repo scripts by walking its own parents. ONE owner for that walk: adding a
    second copy for the version-verdict module produced a duplicate the ratchet caught,
    and the two copies differed only in their candidate list and their sentinel name.
    """
    script = Path(__file__).resolve()
    for ancestor in script.parents:
        for rel in candidates:
            candidate = ancestor.joinpath(*rel)
            if candidate.is_file():
                return candidate
    return Path(missing)


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _find_gather_adapter_script() -> Path:
    return _find_repo_script(
        ("skills", "public", "gather", "scripts", "resolve_adapter.py"),
        ("skills", "gather", "scripts", "resolve_adapter.py"),
        missing="__missing_gather_resolve_adapter__.py",
    )


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
    # GUARDED AT THE READ SITE, and the flip here runs in the PERMISSIVE direction on an
    # external-fetch boundary. Measured at `e1c93ba17`: a repo declaring
    # `gather_provider.github.mode: none` -- "this repo has no GitHub path" -- resolved to
    # `direct-cli` under `version: 9`, routing `github.com` to `github-grant-or-cli`
    # instead of `github-missing-capability`. The repo said it had no path; the router
    # offered to take one.
    #
    # The `except Exception -> "direct-cli"` fallback above is DELIBERATELY LEFT: a missing
    # resolver or an unloadable module is not "the repo declared something this reader
    # ignored", and degrading there keeps web fetch working in a checkout that ships no
    # gather skill. This guard fires only on the state where a declaration exists and was
    # not honored.
    verdict_path = _find_repo_script(
        ("scripts", "adapters", "adapter_version_verdict.py"),
        missing="__missing_adapter_version_verdict__.py",
    )
    if verdict_path.is_file():
        verdict = _load_module(verdict_path, "web_fetch_adapter_version_verdict")
        if verdict is not None:
            refusal = verdict.unspeakable_version_message(
                module.load_adapter, repo_root, adapter_name="gather-adapter.yaml"
            )
            if refusal is not None:
                raise SystemExit(refusal)
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
