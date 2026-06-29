#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
import runpy
import sys
from pathlib import Path
from types import SimpleNamespace
from urllib.parse import urlparse

SCRIPT_DIR = Path(__file__).resolve().parent
SUPPORT_WEB_FETCH = SCRIPT_DIR.parents[2] / "support" / "web-fetch" / "scripts" / "route_public_fetch.py"
ENVELOPE = SimpleNamespace(
    **runpy.run_path(str(SCRIPT_DIR.parents[2] / "shared" / "scripts" / "run_plan_envelope.py"))
)
EXACT_SOURCE_CONTRACTS = {
    "twitter-syndication": {
        "required": True,
        "owner": "support/web-fetch/twitter_exact_source",
        "route_order": ("tweet-result", "oembed"),
        "terminal_verdicts": ("exact-fetched", "exact-blocked", "exact-unavailable"),
        "terminal_categories": ("acquired", "provider-required", "auth-browser-required", "unsupported"),
        "substitution_policy": "never_as_original",
    },
    "reddit-feed": {
        "required": False,
        "owner": "support/web-fetch/reddit_source",
        "route_order": ("rss-feed", "json-endpoint", "direct-page"),
        "terminal_verdicts": (
            "feed-fetched",
            "json-fetched",
            "direct-page-fetched",
            "feed-blocked",
            "feed-unavailable",
        ),
        "substitution_policy": "preserve_source_url_and_do_not_present_search_results_as_the_source",
    },
}


def _load_resolve_adapter():
    spec = importlib.util.spec_from_file_location("gather_resolve_adapter", SCRIPT_DIR / "resolve_adapter.py")
    if spec is None or spec.loader is None:
        raise ImportError("could not load gather resolve_adapter.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_route_module():
    return runpy.run_path(str(SUPPORT_WEB_FETCH))


def _source_kind(url: str) -> str:
    parsed = urlparse(url)
    if parsed.scheme in {"http", "https"}:
        return "public_url"
    return "local_or_unknown"


# Provider-backed hosts gather_plan.py does NOT plan: it only routes public-URL
# fetches, so a Slack/Google Workspace URL would otherwise be silently planned as a
# generic public fetch. Detect them and hand the judge the right adviser instead of
# a misroute (north star: the script briefs the judge). GitHub is excluded — it has
# a real route (github-host-mediated); Notion/other private SaaS go through the
# browser-mediated path, not a dedicated adviser.
_GOOGLE_WORKSPACE_HOSTS = {
    "docs.google.com",
    "drive.google.com",
    "sheets.google.com",
    "slides.google.com",
    "script.google.com",
}


def _provider_redirect(host: str | None) -> dict[str, str] | None:
    host = (host or "").lower()
    if host == "slack.com" or host.endswith(".slack.com"):
        return {
            "source": "slack",
            "adviser": "$SKILL_DIR/scripts/advise_slack_path.py",
            "why": "Slack threads are acquired through the gather-slack provider path, not the public-URL fetch route.",
        }
    if host in _GOOGLE_WORKSPACE_HOSTS:
        return {
            "source": "google_workspace",
            "adviser": "$SKILL_DIR/scripts/advise_google_workspace_path.py",
            "why": "Google Workspace content needs the workspace path adviser (host-mediated > operator export > browser-mediated), not the public-URL fetch route.",
        }
    return None


def _exact_source_contract(route_id: str) -> dict[str, object]:
    contract = EXACT_SOURCE_CONTRACTS.get(route_id)
    if contract is None:
        return {"required": False, "owner": "support/web-fetch", "terminal_verdicts": []}
    return {
        key: list(value) if isinstance(value, tuple) else value
        for key, value in contract.items()
    }


def _required_reads(route_id: str) -> list[dict[str, str]]:
    reads = [
        ENVELOPE.read(
            "references/source-priority.md",
            "keeps primary-source and source-identity decisions explicit",
            trigger="before widening from a named source into search or adjacent material",
        ),
        ENVELOPE.read(
            "references/capability-contract.md",
            "defines access modes, trace preservation, and clean-stop behavior",
            trigger="before interpreting provider access, degradation, or blocked results",
        ),
    ]
    if route_id in {"twitter-syndication", "reddit-feed"}:
        reads.append(
            ENVELOPE.read(
                "../../support/web-fetch/references/routing-table.md",
                "names route ownership and source-specific fallback order without bloating gather core",
                trigger="when a public URL routes through support/web-fetch domain tactics",
            )
        )
    return reads


def build_plan(repo_root: Path, url: str, *, intent: str = "single", browser_mode: str = "auto") -> dict[str, object]:
    adapter_module = _load_resolve_adapter()
    adapter = adapter_module.load_adapter(repo_root)
    route_module = _load_route_module()
    route = route_module["route_for_url"](url, repo_root=repo_root)
    route_id = str(route["route_id"])
    command = [
        "python3",
        "$SKILL_DIR/scripts/gather_public_url.py",
        "--repo-root",
        str(repo_root),
        "--url",
        url,
        "--intent",
        intent,
        "--browser-mode",
        browser_mode,
    ]
    redirect = _provider_redirect(route.get("normalized_host"))
    if redirect is not None:
        next_action = ENVELOPE.next_action(
            "redirect_to_provider_adviser",
            command=["python3", redirect["adviser"], "--repo-root", str(repo_root)],
            redirect=(
                f"{redirect['source']} source: gather_plan.py only plans the public-URL fetch route, so "
                f"run the named adviser and follow the provider path instead. {redirect['why']}"
            ),
            stop_when="the adviser reports the provider mode is none/unavailable and no honest fallback (operator export or labeled browser-mediated) remains",
        )
    else:
        next_action = ENVELOPE.next_action(
            "fetch_public_url",
            command=command,
            execute_flag="--execute writes the durable record when acquisition succeeds, when a route explicitly allows an honest partial record, or when an exact-source route reaches a terminal identity verdict",
            stop_when="typed blocked, unsupported, missing capability, or exact-source unavailable result answers the acquisition boundary",
        )
    return ENVELOPE.build_envelope(
        schema_version="gather.run_plan.v1",
        required_reads=_required_reads(route_id),
        next_action=next_action,
        gate_packets=[
            ENVELOPE.gate_packet(
                "adapter-readiness",
                "deterministic adapter parser; trust failures",
                status="pass" if adapter.get("valid") else "fail",
            ),
            ENVELOPE.gate_packet(
                "acquisition-trace",
                "deterministic route trace; agent judges whether the typed verdict answers the user",
                cost_tier="route-dependent",
                command="gather_public_url.py emits acquisition attempts, selected attempt, source_identity, and write_record",
            ),
        ],
        ok=bool(adapter.get("valid")),
        repo_root=str(repo_root),
        source={
            "kind": _source_kind(url),
            "url": url,
            "host": route.get("normalized_host"),
        },
        adapter={
            "valid": adapter.get("valid"),
            "path": adapter.get("path"),
            "output_dir": adapter.get("data", {}).get("output_dir"),
            "provider_modes": adapter.get("data", {}).get("gather_provider"),
        },
        route=route,
        exact_source=_exact_source_contract(route_id),
        source_owner=redirect,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Plan a gather run before acquiring or refreshing a source.")
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--url", required=True)
    parser.add_argument("--intent", choices=("single", "collect"), default="single")
    parser.add_argument("--browser-mode", choices=("auto", "off", "always"), default="auto")
    args = parser.parse_args()
    payload = build_plan(args.repo_root.resolve(), args.url, intent=args.intent, browser_mode=args.browser_mode)
    sys.stdout.write(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
