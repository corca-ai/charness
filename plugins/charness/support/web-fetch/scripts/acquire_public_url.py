#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import time
import urllib.request
from pathlib import Path
from typing import Sequence
from urllib.parse import urlparse

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import browser_fallback_stages  # noqa: E402
import twitter_exact_source  # noqa: E402
import youtube_browser_ui  # noqa: E402
import youtube_source  # noqa: E402
from acquisition_trace_lib import (  # noqa: E402
    AcquisitionAttempt,
    disposition_for_attempts,
    has_stage,
    has_success,
    last_content_attempt,
    payload,
    should_stop,
    skip_attempt,
)
from classify_fetch_response import classify, extract_persistable_text  # noqa: E402
from route_public_fetch import route_for_url  # noqa: E402


def _read_direct(url: str, *, timeout: int, direct_response_file: Path | None) -> tuple[str, str | None]:
    if direct_response_file is not None:
        return direct_response_file.read_text(encoding="utf-8"), None
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (compatible; charness-web-fetch/1.0)",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            charset = response.headers.get_content_charset() or "utf-8"
            return response.read().decode(charset, errors="replace"), None
    except Exception as exc:
        return "", f"{type(exc).__name__}:{str(exc)[:200]}"


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


def _domain_route_fetcher(args: argparse.Namespace):
    seed_path = getattr(args, "domain_route_response_file", None)
    seed_map = json.loads(seed_path.read_text(encoding="utf-8")) if seed_path is not None else None
    return twitter_exact_source.make_fetcher(
        seed_map,
        live=bool(getattr(args, "live_domain_route", False)),
        live_fetch=lambda endpoint_url: _read_direct(endpoint_url, timeout=args.timeout, direct_response_file=None),
    )


def _attempt_from_text(
    *,
    stage_id: str,
    tool_id: str | None,
    text: str,
    elapsed_s: float,
    intent: str,
    expect_text: list[str],
    expect_regex: list[str],
    expect_json_field: list[str],
    error: str | None = None,
    details: dict[str, object] | None = None,
    content_format: str = "text",
) -> AcquisitionAttempt:
    classification = classify(
        text,
        intent=intent,
        expect_text=expect_text,
        expect_regex=expect_regex,
        expect_json_field=expect_json_field,
    )
    classification_status = str(classification["status"])
    status = classification_status
    if error is not None and classification_status != "invalid-proof":
        status = "error"
    content_text = extract_persistable_text(text, content_format=content_format)
    return AcquisitionAttempt(
        stage_id=stage_id,
        tool_id=tool_id,
        status=status,
        confidence=str(classification.get("confidence", "none")),
        elapsed_s=elapsed_s,
        error=error,
        output_chars=len(text),
        classification=classification,
        details=details or {},
        content_text=content_text,
        content_format=content_format,
    )


def _should_try_defuddle(route_id: str, attempts: list[AcquisitionAttempt]) -> tuple[bool, str | None]:
    if route_id not in {"direct-then-fallback", "reader-fallback", "naver-blog-mobile"}:
        return False, "route-not-applicable"
    last = last_content_attempt(attempts)
    if last is not None and last.status not in {"partial-content", "empty-spa", "unclear", "error", "captcha", "error-page"}:
        return False, "prior-stage-sufficient"
    if shutil.which("defuddle") is None:
        return False, "missing-tool"
    return True, None


def _should_try_browser(
    route_id: str,
    attempts: list[AcquisitionAttempt],
    *,
    browser_mode: str,
) -> tuple[bool, str | None]:
    if browser_mode == "off":
        return False, "browser-mode-off"
    last = last_content_attempt(attempts)
    if last is not None and last.status not in {"partial-content", "empty-spa", "captcha", "unclear", "error", "error-page"}:
        return False, "prior-stage-sufficient"
    if shutil.which("agent-browser") is None:
        return False, "missing-tool"
    if browser_mode == "always":
        return True, None
    if route_id not in {"direct-then-fallback", "reader-fallback", "naver-blog-mobile"}:
        return False, "route-not-applicable"
    if last is None:
        return False, "no-prior-content"
    return True, None


def _should_try_youtube_browser(
    route_id: str,
    attempts: list[AcquisitionAttempt],
    *,
    browser_mode: str,
) -> tuple[bool, str | None]:
    if route_id != "yt-dlp-metadata":
        return False, "route-not-applicable"
    if browser_mode == "off":
        return False, "browser-mode-off"
    for attempt in attempts:
        if (
            attempt.stage_id == youtube_source.STAGE_ID
            and attempt.status == "success"
            and attempt.details.get("source_type") == "youtube-transcript"
        ):
            return False, "prior-stage-sufficient"
    last = last_content_attempt(attempts)
    if last is not None and last.stage_id == "direct-public-fetch" and should_stop(last, proof_required=False):
        return False, "prior-stage-sufficient"
    if shutil.which("agent-browser") is None:
        return False, "missing-tool"
    return True, None


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


def _direct_attempt_sufficient(
    route: dict[str, object],
    attempt: AcquisitionAttempt,
    *,
    proof_required: bool,
) -> bool:
    if not should_stop(attempt, proof_required=proof_required):
        return False
    if route.get("route_id") == "yt-dlp-metadata" and attempt.confidence != "strong":
        return False
    return True


def acquire(args: argparse.Namespace) -> dict[str, object]:
    parsed = urlparse(args.url)
    if parsed.scheme not in {"http", "https"}:
        return _invalid_scheme_payload(args, parsed)
    route = route_for_url(args.url, repo_root=args.repo_root)
    attempts: list[AcquisitionAttempt] = []
    proof_required = bool(args.expect_text or args.expect_regex or args.expect_json_field)
    started = time.monotonic()
    text, error = _read_direct(args.url, timeout=args.timeout, direct_response_file=args.direct_response_file)
    attempts.append(
        _attempt_from_text(
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
    _run_domain_specific_route(args, route, attempts)
    if direct_attempt.status == "invalid-proof":
        return _payload_for(args, route, attempts, "error")
    if _direct_attempt_sufficient(route, direct_attempt, proof_required=proof_required):
        return _payload_for(args, route, attempts, "success")
    try_youtube_browser, youtube_browser_skip_reason = _should_try_youtube_browser(
        str(route["route_id"]), attempts, browser_mode=args.browser_mode
    )
    if try_youtube_browser:
        youtube_browser_payload = browser_fallback_stages.run_youtube_browser_stage(
            args,
            route,
            attempts,
            proof_required=proof_required,
            script_dir=SCRIPT_DIR,
            run_command=_run_command,
            payload_for=_payload_for,
        )
        if youtube_browser_payload is not None:
            return youtube_browser_payload
    elif youtube_browser_skip_reason in {"missing-tool", "browser-mode-off"} and has_stage(
        route, youtube_browser_ui.UI_STAGE_ID
    ):
        attempts.append(skip_attempt(youtube_browser_ui.UI_STAGE_ID, "agent-browser", reason=youtube_browser_skip_reason))
    if has_success(attempts, proof_required=proof_required):
        return _payload_for(args, route, attempts, "success")
    try_defuddle, defuddle_skip_reason = _should_try_defuddle(str(route["route_id"]), attempts)
    if try_defuddle:
        started = time.monotonic()
        text, error = _run_command(["defuddle", "parse", args.url, "--markdown"], timeout=args.timeout)
        attempts.append(
            _attempt_from_text(
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
    elif defuddle_skip_reason == "missing-tool" and has_stage(route, "defuddle-reader-extraction"):
        attempts.append(skip_attempt("defuddle-reader-extraction", "defuddle", reason=defuddle_skip_reason))
    try_browser, browser_skip_reason = _should_try_browser(str(route["route_id"]), attempts, browser_mode=args.browser_mode)
    if try_browser:
        browser_payload = browser_fallback_stages.run_generic_browser_stage(
            args,
            route,
            attempts,
            proof_required=proof_required,
            script_dir=SCRIPT_DIR,
            run_command=_run_command,
            payload_for=_payload_for,
        )
        if browser_payload is not None:
            return browser_payload
    elif browser_skip_reason in {"missing-tool", "browser-mode-off"} and has_stage(route, "agent-browser-render-recon"):
        attempts.append(skip_attempt("agent-browser-render-recon", "agent-browser", reason=browser_skip_reason))
        if args.intent == "collect" and has_stage(route, "agent-browser-network-recon"):
            attempts.append(skip_attempt("agent-browser-network-recon", "agent-browser", reason=browser_skip_reason))
    return _payload_for(args, route, attempts, disposition_for_attempts(attempts))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--intent", choices=("single", "collect"), default="single")
    parser.add_argument("--browser-mode", choices=("auto", "off", "always"), default="auto")
    parser.add_argument("--timeout", type=int, default=20)
    parser.add_argument("--direct-response-file", type=Path)
    parser.add_argument("--domain-route-response-file", type=Path, help="JSON map {endpoint_url: {text, error}} seeding the domain-specific exact-source stage (no live fetch)")
    parser.add_argument("--live-domain-route", action="store_true", help="Allow live network fetch of domain-specific exact-source endpoints (operator-authorized; off by default)")
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
