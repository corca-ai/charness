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

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from classify_fetch_response import classify  # noqa: E402
from route_public_fetch import route_for_url  # noqa: E402

SUCCESS_STATUSES = {"success"}


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
    if attempt.status not in SUCCESS_STATUSES:
        return False
    if proof_required:
        return attempt.confidence == "strong"
    return attempt.confidence in {"strong", "weak"}


def _has_success(attempts: list[AcquisitionAttempt], *, proof_required: bool) -> bool:
    return any(_should_stop(attempt, proof_required=proof_required) for attempt in attempts)


def _should_try_defuddle(route_id: str, attempts: list[AcquisitionAttempt]) -> bool:
    if shutil.which("defuddle") is None:
        return False
    if route_id not in {"direct-then-fallback", "reader-fallback", "naver-blog-mobile"}:
        return False
    if not attempts:
        return True
    last = attempts[-1]
    return last.status in {"partial-content", "empty-spa", "unclear", "error"}


def _should_try_browser(
    route_id: str,
    attempts: list[AcquisitionAttempt],
    *,
    browser_mode: str,
) -> bool:
    if browser_mode == "off":
        return False
    if shutil.which("agent-browser") is None:
        return False
    if browser_mode == "always":
        return True
    if route_id not in {"direct-then-fallback", "reader-fallback", "naver-blog-mobile"}:
        return False
    if not attempts:
        return False
    last = attempts[-1]
    return last.status in {"partial-content", "empty-spa", "captcha", "unclear", "error"}


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
    if _should_stop(attempts[-1], proof_required=proof_required):
        return _payload(args.url, route, attempts, "success")

    if _should_try_defuddle(str(route["route_id"]), attempts):
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

    if _should_try_browser(str(route["route_id"]), attempts, browser_mode=args.browser_mode):
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
                    status="success" if network_error is None else "error",
                    confidence="weak" if network_text.strip() else "none",
                    elapsed_s=_elapsed(started),
                    error=network_error,
                    output_chars=len(network_text),
                    details=network_details,
                )
            )
        if _has_success(attempts, proof_required=proof_required):
            return _payload(args.url, route, attempts, "success")

    return _payload(args.url, route, attempts, "degraded")


def _payload(
    url: str,
    route: dict[str, object],
    attempts: list[AcquisitionAttempt],
    disposition: str,
) -> dict[str, object]:
    return {
        "source_url": url,
        "route": route,
        "disposition": disposition,
        "attempts": [attempt.to_dict() for attempt in attempts],
        "final_status": attempts[-1].status if attempts else "unknown",
        "final_confidence": attempts[-1].confidence if attempts else "none",
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
