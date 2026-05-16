#!/usr/bin/env python3

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import time
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Sequence
from urllib.parse import urlparse

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from classify_fetch_response import classify  # noqa: E402
from route_public_fetch import route_for_url  # noqa: E402

SUCCESS_STATUSES = {"success"}
BLOCKED_STATUSES = {"captcha", "login-wall", "error-page"}


@dataclass
class AcquisitionAttempt:
    stage_id: str
    tool_id: str | None
    status: str
    confidence: str = "none"
    elapsed_s: float = 0.0
    error: str | None = None
    output_chars: int = 0
    classification: dict[str, object] | None = None
    details: dict[str, object] = field(default_factory=dict)

    def to_dict(self) -> dict[str, object]:
        payload: dict[str, object] = {
            "stage_id": self.stage_id,
            "tool_id": self.tool_id,
            "status": self.status,
            "confidence": self.confidence,
            "elapsed_s": self.elapsed_s,
            "output_chars": self.output_chars,
        }
        if self.error:
            payload["error"] = self.error
        if self.classification is not None:
            payload["classification"] = self.classification
        if self.details:
            payload["details"] = self.details
        return payload


def _timer() -> float:
    return time.monotonic()


def _elapsed(start: float) -> float:
    return round(time.monotonic() - start, 3)


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


def _classify_text(
    text: str,
    *,
    intent: str,
    expect_text: list[str],
    expect_regex: list[str],
    expect_json_field: list[str],
) -> dict[str, object]:
    return classify(
        text,
        intent=intent,
        expect_text=expect_text,
        expect_regex=expect_regex,
        expect_json_field=expect_json_field,
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
) -> AcquisitionAttempt:
    classification = _classify_text(
        text,
        intent=intent,
        expect_text=expect_text,
        expect_regex=expect_regex,
        expect_json_field=expect_json_field,
    )
    return AcquisitionAttempt(
        stage_id=stage_id,
        tool_id=tool_id,
        status=str(classification["status"]) if error is None else "error",
        confidence=str(classification.get("confidence", "none")),
        elapsed_s=elapsed_s,
        error=error,
        output_chars=len(text),
        classification=classification,
        details=details or {},
    )


def _should_stop(attempt: AcquisitionAttempt, *, proof_required: bool) -> bool:
    if attempt.details.get("diagnostic"):
        return False
    if attempt.status not in SUCCESS_STATUSES:
        return False
    if proof_required:
        return attempt.confidence == "strong"
    return attempt.confidence in {"strong", "weak"}


def _has_success(attempts: list[AcquisitionAttempt], *, proof_required: bool) -> bool:
    return any(_should_stop(attempt, proof_required=proof_required) for attempt in attempts)


def _last_content_attempt(attempts: list[AcquisitionAttempt]) -> AcquisitionAttempt | None:
    for attempt in reversed(attempts):
        if attempt.status == "skipped" or attempt.details.get("diagnostic"):
            continue
        return attempt
    return None


def _skip_attempt(stage_id: str, tool_id: str | None, *, reason: str) -> AcquisitionAttempt:
    return AcquisitionAttempt(
        stage_id=stage_id,
        tool_id=tool_id,
        status="skipped",
        confidence="none",
        details={"reason": reason},
    )


def _has_stage(route: dict[str, object], stage_id: str) -> bool:
    plan = route.get("acquisition_plan") or []
    return any(isinstance(stage, dict) and stage.get("stage_id") == stage_id for stage in plan)


def _should_try_defuddle(route_id: str, attempts: list[AcquisitionAttempt]) -> tuple[bool, str | None]:
    if route_id not in {"direct-then-fallback", "reader-fallback", "naver-blog-mobile"}:
        return False, "route-not-applicable"
    last = _last_content_attempt(attempts)
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
    last = _last_content_attempt(attempts)
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


def _browser_session_name(url: str) -> str:
    digest = hashlib.sha256(url.encode("utf-8")).hexdigest()[:12]
    return f"charness-gather-{digest}"


def _run_browser_text(url: str, *, timeout: int) -> tuple[str, str | None, dict[str, object]]:
    session = _browser_session_name(url)
    details: dict[str, object] = {"session": session}
    for command in (
        ["agent-browser", "--session", session, "open", url],
        ["agent-browser", "--session", session, "wait", "1000"],
    ):
        _stdout, error = _run_command(command, timeout=timeout)
        if error:
            return "", error, details
    text, error = _run_command(
        ["agent-browser", "--session", session, "get", "text", "body"],
        timeout=timeout,
    )
    if error:
        return text, error, details
    return text, None, details


def _run_browser_network(url: str, *, timeout: int) -> tuple[str, str | None, dict[str, object]]:
    session = _browser_session_name(url)
    requests_text, requests_error = _run_command(
        ["agent-browser", "--session", session, "network", "requests", "--filter", "api|graphql|json"],
        timeout=timeout,
    )
    candidates = [
        line.strip()
        for line in requests_text.splitlines()
        if line.strip()
    ][:20]
    details: dict[str, object] = {"session": session, "network_candidates": candidates}
    return requests_text, requests_error, details


def acquire(args: argparse.Namespace) -> dict[str, object]:
    parsed = urlparse(args.url)
    if parsed.scheme not in {"http", "https"}:
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
        return _payload(args.url, route, attempts, "error")

    route = route_for_url(args.url, repo_root=args.repo_root)
    attempts: list[AcquisitionAttempt] = []
    proof_required = bool(args.expect_text or args.expect_regex or args.expect_json_field)

    started = _timer()
    text, error = _read_direct(args.url, timeout=args.timeout, direct_response_file=args.direct_response_file)
    attempts.append(
        _attempt_from_text(
            stage_id="direct-public-fetch",
            tool_id=None,
            text=text,
            elapsed_s=_elapsed(started),
            error=error,
            intent=args.intent,
            expect_text=args.expect_text,
            expect_regex=args.expect_regex,
            expect_json_field=args.expect_json_field,
        )
    )
    direct_attempt = attempts[-1]
    if _has_stage(route, "domain-specific-route"):
        attempts.append(_skip_attempt("domain-specific-route", None, reason="not-implemented"))
    if direct_attempt.status == "invalid-proof":
        return _payload(args.url, route, attempts, "error")
    if _should_stop(direct_attempt, proof_required=proof_required):
        return _payload(args.url, route, attempts, "success")

    try_defuddle, defuddle_skip_reason = _should_try_defuddle(str(route["route_id"]), attempts)
    if try_defuddle:
        started = _timer()
        text, error = _run_command(["defuddle", "parse", args.url, "--markdown"], timeout=args.timeout)
        attempts.append(
            _attempt_from_text(
                stage_id="defuddle-reader-extraction",
                tool_id="defuddle",
                text=text,
                elapsed_s=_elapsed(started),
                error=error,
                intent=args.intent,
                expect_text=args.expect_text,
                expect_regex=args.expect_regex,
                expect_json_field=args.expect_json_field,
            )
        )
        if _has_success(attempts, proof_required=proof_required):
            return _payload(args.url, route, attempts, "success")
    elif defuddle_skip_reason == "missing-tool" and _has_stage(route, "defuddle-reader-extraction"):
        attempts.append(_skip_attempt("defuddle-reader-extraction", "defuddle", reason=defuddle_skip_reason))

    try_browser, browser_skip_reason = _should_try_browser(str(route["route_id"]), attempts, browser_mode=args.browser_mode)
    if try_browser:
        started = _timer()
        text, error, details = _run_browser_text(args.url, timeout=args.timeout)
        attempts.append(
            _attempt_from_text(
                stage_id="agent-browser-render-recon",
                tool_id="agent-browser",
                text=text,
                elapsed_s=_elapsed(started),
                error=error,
                intent=args.intent,
                expect_text=args.expect_text,
                expect_regex=args.expect_regex,
                expect_json_field=args.expect_json_field,
                details=details,
            )
        )
        if args.intent == "collect":
            started = _timer()
            network_text, network_error, network_details = _run_browser_network(args.url, timeout=args.timeout)
            attempts.append(
                AcquisitionAttempt(
                    stage_id="agent-browser-network-recon",
                    tool_id="agent-browser",
                    status="diagnostic" if network_error is None else "error",
                    confidence="weak" if network_text.strip() else "none",
                    elapsed_s=_elapsed(started),
                    error=network_error,
                    output_chars=len(network_text),
                    details={**network_details, "diagnostic": True},
                )
            )
        if _has_success(attempts, proof_required=proof_required):
            return _payload(args.url, route, attempts, "success")
    elif browser_skip_reason in {"missing-tool", "browser-mode-off"} and _has_stage(route, "agent-browser-render-recon"):
        attempts.append(_skip_attempt("agent-browser-render-recon", "agent-browser", reason=browser_skip_reason))
        if args.intent == "collect" and _has_stage(route, "agent-browser-network-recon"):
            attempts.append(_skip_attempt("agent-browser-network-recon", "agent-browser", reason=browser_skip_reason))

    return _payload(args.url, route, attempts, _disposition_for_attempts(attempts))


def _selected_attempt(attempts: list[AcquisitionAttempt]) -> AcquisitionAttempt | None:
    successes = [attempt for attempt in attempts if _should_stop(attempt, proof_required=False)]
    if successes:
        strong = [attempt for attempt in successes if attempt.confidence == "strong"]
        return (strong or successes)[-1]
    return _last_content_attempt(attempts)


def _disposition_for_attempts(attempts: list[AcquisitionAttempt]) -> str:
    selected = _selected_attempt(attempts)
    if selected is None:
        return "degraded"
    if selected.status == "invalid-proof":
        return "error"
    if selected.status == "success":
        return "success"
    if selected.status in BLOCKED_STATUSES:
        return "blocked"
    return "degraded"


def _payload(
    url: str,
    route: dict[str, object],
    attempts: list[AcquisitionAttempt],
    disposition: str,
) -> dict[str, object]:
    selected = _selected_attempt(attempts)
    selected_payload = selected.to_dict() if selected is not None else None
    return {
        "source_url": url,
        "route": route,
        "disposition": disposition,
        "attempts": [attempt.to_dict() for attempt in attempts],
        "selected_attempt": selected_payload,
        "final_status": selected.status if selected is not None else "unknown",
        "final_confidence": selected.confidence if selected is not None else "none",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--intent", choices=("single", "collect"), default="single")
    parser.add_argument("--browser-mode", choices=("auto", "off", "always"), default="auto")
    parser.add_argument("--timeout", type=int, default=20)
    parser.add_argument("--direct-response-file", type=Path)
    parser.add_argument("--expect-text", action="append", default=[])
    parser.add_argument("--expect-regex", action="append", default=[])
    parser.add_argument("--expect-json-field", action="append", default=[])
    args = parser.parse_args()
    print(json.dumps(acquire(args), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
