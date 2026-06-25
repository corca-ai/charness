#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Sequence
from urllib.parse import urlparse

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import browser_fallback_stages  # noqa: E402
import impersonated_fetch_stage  # noqa: E402
import patchright_headless_stage  # noqa: E402
import reddit_source  # noqa: E402
import twitter_exact_source  # noqa: E402
import youtube_browser_ui  # noqa: E402
import youtube_source  # noqa: E402
from acquire_public_url_policy import (  # noqa: E402
    direct_attempt_sufficient as _direct_attempt_sufficient,
)
from acquire_public_url_policy import (  # noqa: E402
    should_try_browser as _should_try_browser,
)
from acquire_public_url_policy import (  # noqa: E402
    should_try_defuddle as _should_try_defuddle,
)
from acquire_public_url_policy import (  # noqa: E402
    should_try_impersonated_fetch as _should_try_impersonated_fetch,
)
from acquire_public_url_policy import (  # noqa: E402
    should_try_patchright as _should_try_patchright,
)
from acquire_public_url_policy import (  # noqa: E402
    should_try_youtube_browser as _should_try_youtube_browser,
)
from acquisition_trace_lib import (  # noqa: E402
    AcquisitionAttempt,
    disposition_for_attempts,
    has_stage,
    has_success,
    payload,
    skip_attempt,
)
from route_public_fetch import route_for_url  # noqa: E402
from text_attempts import attempt_from_text  # noqa: E402
from url_reader import read_url  # noqa: E402


def _read_direct(url: str, *, timeout: int, direct_response_file: Path | None) -> tuple[str, str | None]:
    if direct_response_file is not None:
        return direct_response_file.read_text(encoding="utf-8"), None
    return read_url(
        url,
        timeout=timeout,
        headers={
            "User-Agent": "Mozilla/5.0 (compatible; charness-web-fetch/1.0)",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        },
    )


def _run_command(command: Sequence[str], *, timeout: int) -> tuple[str, str | None]:
    try:
        completed = subprocess.run(
            list(command),
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except Exception as exc:
        return "", f"{type(exc).__name__}:{str(exc)[:200]}"
    if completed.returncode != 0:
        stderr = completed.stderr.strip() or completed.stdout.strip()
        return completed.stdout, f"exit={completed.returncode}:{stderr[:200]}"
    return completed.stdout, None


def _positive_int(raw: str) -> int:
    value = int(raw)
    if value < 1:
        raise argparse.ArgumentTypeError("must be a positive integer")
    return value


def _domain_seed_map(args: argparse.Namespace) -> dict | None:
    seed_path = getattr(args, "domain_route_response_file", None)
    return json.loads(seed_path.read_text(encoding="utf-8")) if seed_path is not None else None


def _domain_route_fetcher(args: argparse.Namespace):
    return twitter_exact_source.make_fetcher(
        _domain_seed_map(args),
        live=bool(getattr(args, "live_domain_route", False)),
        live_fetch=lambda endpoint_url: _read_direct(endpoint_url, timeout=args.timeout, direct_response_file=None),
    )


def _seeded_or_live_fetcher(args: argparse.Namespace):
    seed_map = _domain_seed_map(args)

    def fetch(endpoint: dict) -> tuple[str | None, str | None]:
        endpoint_url = endpoint["url"]
        if seed_map is not None and endpoint_url in seed_map:
            entry = seed_map[endpoint_url]
            return entry.get("text"), entry.get("error")
        if seed_map is not None and not getattr(args, "live_domain_route", False):
            return None, "seed-missing"
        return _read_direct(endpoint_url, timeout=args.timeout, direct_response_file=None)

    return fetch


def _invalid_scheme_payload(args: argparse.Namespace, parsed) -> dict[str, object]:
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

    return _payload_for(args, route, attempts, "error")


def _payload_for(
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


def _run_domain_specific_route(
    args: argparse.Namespace,
    route: dict[str, object],
    attempts: list[AcquisitionAttempt],
) -> None:
    if not has_stage(route, "domain-specific-route"):
        return
    if route["route_id"] == "twitter-syndication":
        attempts.extend(twitter_exact_source.run_exact_source_stage(args.url, fetcher=_domain_route_fetcher(args)))
    elif route["route_id"] == "reddit-feed":
        attempts.extend(
            reddit_source.run_reddit_stage(
                args.url,
                fetcher=_seeded_or_live_fetcher(args),
                expect_text=args.expect_text,
                expect_regex=args.expect_regex,
                expect_json_field=args.expect_json_field,
                intent=args.intent,
            )
        )
    elif route["route_id"] == "yt-dlp-metadata" and youtube_source.normalized_host(args.url).endswith(
        ("youtube.com", "youtu.be")
    ):
        attempts.extend(
            youtube_source.run_youtube_stage(
                args.url,
                run_command=lambda command: _run_command(command, timeout=args.timeout),
            )
        )
    else:
        attempts.append(skip_attempt("domain-specific-route", None, reason="not-implemented"))


def _domain_first_payload(args, route, attempts, *, proof_required):
    if route.get("route_id") != "reddit-feed":
        return None
    _run_domain_specific_route(args, route, attempts)
    if has_success(attempts, proof_required=proof_required):
        return _payload_for(args, route, attempts, "success")
    return None


def _try_youtube_browser_payload(args, route, attempts, *, proof_required):
    should_try, skip_reason = _should_try_youtube_browser(str(route["route_id"]), attempts, browser_mode=args.browser_mode)
    if should_try:
        return browser_fallback_stages.run_youtube_browser_stage(
            args,
            route,
            attempts,
            proof_required=proof_required,
            script_dir=SCRIPT_DIR,
            run_command=_run_command,
            payload_for=_payload_for,
        )
    if skip_reason in {"missing-tool", "browser-mode-off"} and has_stage(route, youtube_browser_ui.UI_STAGE_ID):
        attempts.append(skip_attempt(youtube_browser_ui.UI_STAGE_ID, "agent-browser", reason=skip_reason))
    return None


def _try_defuddle_reader(args, route, attempts, *, proof_required):
    should_try, skip_reason = _should_try_defuddle(str(route["route_id"]), attempts)
    if should_try:
        started = time.monotonic()
        text, error = _run_command(["defuddle", "parse", args.url, "--markdown"], timeout=args.timeout)
        attempts.append(
            attempt_from_text(
                stage_id="defuddle-reader-extraction",
                tool_id="defuddle",
                text=text,
                elapsed_s=round(time.monotonic() - started, 3),
                error=error,
                intent=args.intent,
                expect_text=args.expect_text,
                expect_regex=args.expect_regex,
                expect_json_field=args.expect_json_field,
                content_format="markdown",
            )
        )
        if has_success(attempts, proof_required=proof_required):
            return _payload_for(args, route, attempts, "success")
    elif skip_reason == "missing-tool" and has_stage(route, "defuddle-reader-extraction"):
        attempts.append(skip_attempt("defuddle-reader-extraction", "defuddle", reason=skip_reason))
    return None


def _try_impersonated_fetch(args, route, attempts, *, proof_required):
    should_try, skip_reason = _should_try_impersonated_fetch(
        str(route["route_id"]),
        attempts,
        seeded_direct=args.direct_response_file is not None,
    )
    if should_try:
        return impersonated_fetch_stage.run_impersonated_fetch_stage(
            args,
            route,
            attempts,
            proof_required=proof_required,
            payload_for=_payload_for,
        )
    if skip_reason in {"missing-tool", "seeded-direct-fixture"} and has_stage(route, "impersonated-public-fetch"):
        attempts.append(skip_attempt("impersonated-public-fetch", "curl_cffi", reason=skip_reason))
    return None


def _try_patchright_payload(args, route, attempts, *, proof_required):
    should_try, skip_reason = _should_try_patchright(
        str(route["route_id"]),
        attempts,
        browser_mode=args.browser_mode,
        seeded_direct=args.direct_response_file is not None,
    )
    if should_try:
        return patchright_headless_stage.run_patchright_stage(
            args,
            route,
            attempts,
            proof_required=proof_required,
            payload_for=_payload_for,
        )
    if skip_reason in {"missing-tool", "browser-mode-off", "seeded-direct-fixture"} and has_stage(
        route, "patchright-render-recon"
    ):
        attempts.append(skip_attempt("patchright-render-recon", "patchright", reason=skip_reason))
        if args.intent == "collect" and has_stage(route, "patchright-network-recon"):
            attempts.append(skip_attempt("patchright-network-recon", "patchright", reason=skip_reason))
    return None


def _try_generic_browser_payload(args, route, attempts, *, proof_required):
    should_try, skip_reason = _should_try_browser(str(route["route_id"]), attempts, browser_mode=args.browser_mode)
    if should_try:
        return browser_fallback_stages.run_generic_browser_stage(
            args,
            route,
            attempts,
            proof_required=proof_required,
            script_dir=SCRIPT_DIR,
            run_command=_run_command,
            payload_for=_payload_for,
        )
    if skip_reason in {"missing-tool", "browser-mode-off"} and has_stage(route, "agent-browser-render-recon"):
        attempts.append(skip_attempt("agent-browser-render-recon", "agent-browser", reason=skip_reason))
        if args.intent == "collect" and has_stage(route, "agent-browser-network-recon"):
            attempts.append(skip_attempt("agent-browser-network-recon", "agent-browser", reason=skip_reason))
    return None


def acquire(args: argparse.Namespace) -> dict[str, object]:
    parsed = urlparse(args.url)
    if parsed.scheme not in {"http", "https"}:
        return _invalid_scheme_payload(args, parsed)
    route = route_for_url(args.url, repo_root=args.repo_root)
    attempts: list[AcquisitionAttempt] = []
    proof_required = bool(args.expect_text or args.expect_regex or args.expect_json_field)
    domain_first_payload = _domain_first_payload(args, route, attempts, proof_required=proof_required)
    if domain_first_payload is not None:
        return domain_first_payload
    started = time.monotonic()
    text, error = _read_direct(args.url, timeout=args.timeout, direct_response_file=args.direct_response_file)
    attempts.append(
        attempt_from_text(
            stage_id="direct-public-fetch",
            tool_id=None,
            text=text,
            elapsed_s=round(time.monotonic() - started, 3),
            error=error,
            intent=args.intent,
            expect_text=args.expect_text,
            expect_regex=args.expect_regex,
            expect_json_field=args.expect_json_field,
        )
    )
    direct_attempt = attempts[-1]
    if route.get("route_id") != "reddit-feed":
        _run_domain_specific_route(args, route, attempts)
    if direct_attempt.status == "invalid-proof":
        return _payload_for(args, route, attempts, "error")
    if _direct_attempt_sufficient(route, direct_attempt, proof_required=proof_required):
        return _payload_for(args, route, attempts, "success")
    youtube_browser_payload = _try_youtube_browser_payload(args, route, attempts, proof_required=proof_required)
    if youtube_browser_payload is not None:
        return youtube_browser_payload
    if has_success(attempts, proof_required=proof_required):
        return _payload_for(args, route, attempts, "success")
    impersonated_payload = _try_impersonated_fetch(args, route, attempts, proof_required=proof_required)
    if impersonated_payload is not None:
        return impersonated_payload
    defuddle_payload = _try_defuddle_reader(args, route, attempts, proof_required=proof_required)
    if defuddle_payload is not None:
        return defuddle_payload
    patchright_payload = _try_patchright_payload(args, route, attempts, proof_required=proof_required)
    if patchright_payload is not None:
        return patchright_payload
    browser_payload = _try_generic_browser_payload(args, route, attempts, proof_required=proof_required)
    if browser_payload is not None:
        return browser_payload
    return _payload_for(args, route, attempts, disposition_for_attempts(attempts))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--intent", choices=("single", "collect"), default="single")
    parser.add_argument("--browser-mode", choices=("auto", "off", "always"), default="auto")
    parser.add_argument("--timeout", type=int, default=20)
    parser.add_argument("--direct-response-file", type=Path)
    parser.add_argument("--domain-route-response-file", type=Path, help="JSON map {endpoint_url: {text, error}} seeding the domain-specific route; missing seeded endpoints do not fetch live unless --live-domain-route is set")
    parser.add_argument("--live-domain-route", action="store_true", help="Allow live network fetch for seeded-missing exact-source/domain-specific endpoints when the route supports it")
    parser.add_argument("--expect-text", action="append", default=[])
    parser.add_argument("--expect-regex", action="append", default=[])
    parser.add_argument("--expect-json-field", action="append", default=[])
    parser.add_argument("--include-selected-content", action="store_true")
    parser.add_argument("--selected-content-max-chars", type=_positive_int, default=200_000)
    args = parser.parse_args()
    print(json.dumps(acquire(args), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
