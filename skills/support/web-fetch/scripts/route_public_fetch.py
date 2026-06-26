#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from route_public_fetch_routes import (  # noqa: E402
    GITHUB_ROUTE_FOR_MODE,
    ROUTES,
    host_matches,
    normalized_host,
    resolve_github_mode,
    route_id_for_host,
)
from route_stage_catalog import (  # noqa: E402
    FALLBACK_ORDER,
    direct_stage,
    domain_stage,
    reader_fallback_stages,
    terminal_stages,
    youtube_browser_stage,
)


def route_for_url(url: str, *, repo_root: Path | None = None, github_mode: str | None = None) -> dict[str, object]:
    host = normalized_host(url)
    effective_github_mode = github_mode if github_mode in GITHUB_ROUTE_FOR_MODE else resolve_github_mode(repo_root)
    route = ROUTES[route_id_for_host(host, github_mode=effective_github_mode)]

    payload: dict[str, object] = {
        "input_url": url,
        "normalized_host": host,
        "route_id": route.route_id,
        "route_family": route.route_family,
        "summary": route.summary,
        "required_tools": list(route.required_tools),
        "access_modes": list(route.access_modes),
        "fallback_order": list(FALLBACK_ORDER),
        "acquisition_plan": acquisition_plan_for_route(route.route_id),
        "notes": list(route.notes),
    }
    if host_matches(host, ("github.com",)):
        payload["github_mode"] = effective_github_mode
    return payload


def acquisition_plan_for_route(route_id: str) -> list[dict[str, object]]:
    if route_id == "reddit-feed":
        return [
            domain_stage(None)
            | {
                "when": "Try Reddit RSS, then JSON, before raw page fallback.",
                "proof": "source-bound feed/json response plus optional positive proof expectations",
            },
            direct_stage()
            | {
                "when": "Use raw Reddit page only after RSS/JSON cannot satisfy the request.",
            },
            *terminal_stages(),
        ]
    plan: list[dict[str, object]] = [direct_stage()]
    if route_id in {
        "twitter-syndication",
        "hacker-news-firebase",
        "stackexchange-api",
        "github-grant-or-cli",
        "github-host-mediated",
        "github-missing-capability",
        "yt-dlp-metadata",
        "naver-blog-mobile",
    }:
        tool_id = ROUTES[route_id].required_tools[0] if ROUTES[route_id].required_tools else None
        plan.append(domain_stage(tool_id))
    if route_id == "yt-dlp-metadata":
        plan.append(youtube_browser_stage())
    if route_id in {"reader-fallback", "direct-then-fallback", "naver-blog-mobile"}:
        plan.extend(reader_fallback_stages())
    plan.extend(terminal_stages())
    return plan


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    print(json.dumps(route_for_url(args.url, repo_root=args.repo_root), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
