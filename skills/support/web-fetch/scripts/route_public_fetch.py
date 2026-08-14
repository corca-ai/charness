#!/usr/bin/env python3

from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))


def load_yaml_output():
    """Load the shared YAML renderer from the nearest tree root, by path.

    The helper is `<repo>/scripts/yaml_output.py` in the authoring tree and
    `<plugin-root>/scripts/yaml_output.py` once exported, which sit at different
    depths from a support package, so the root is walked to rather than counted.
    The walk is BOUNDED for the reason `authoring_script_shim.locate` records:
    an unbounded one climbs past the package into the CONSUMING repository and
    would execute whatever `scripts/yaml_output.py` it found there."""
    directory = SCRIPT_DIR
    for _ in range(5):
        directory = directory.parent
        candidate = directory / "scripts" / "yaml_output.py"
        if candidate.is_file():
            spec = importlib.util.spec_from_file_location("charness_yaml_output", candidate)
            if spec is None or spec.loader is None:
                break
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module
    raise ImportError("scripts/yaml_output.py not found within 5 ancestors of this script")

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
    content_negotiated_markdown_stage,
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
            content_negotiated_markdown_stage(),
            *terminal_stages(),
        ]
    plan: list[dict[str, object]] = [direct_stage(), content_negotiated_markdown_stage()]
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
    parser.add_argument("--url", required=True, help="Public URL whose acquisition route should be resolved.")
    parser.add_argument("--repo-root", type=Path, default=Path.cwd(), help="Repository root for capability and GitHub mode resolution.")
    args = parser.parse_args()
    load_yaml_output().emit_yaml(route_for_url(args.url, repo_root=args.repo_root))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
