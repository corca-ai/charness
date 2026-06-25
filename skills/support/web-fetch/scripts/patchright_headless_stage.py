"""Headless Patchright acquisition stages."""

from __future__ import annotations

import importlib.util
import re
import time
from typing import Callable

from acquisition_trace_lib import AcquisitionAttempt, has_success
from text_attempts import attempt_from_text

PayloadFor = Callable[[object, dict[str, object], list[AcquisitionAttempt], str], dict[str, object]]

NETWORK_CANDIDATE_RE = re.compile(r"(?:/api/|/graphql|\.json(?:\?|$))", re.IGNORECASE)


def is_available() -> bool:
    return importlib.util.find_spec("patchright") is not None


def _launch_args(channel: str | None) -> dict[str, object]:
    args: dict[str, object] = {"headless": True}
    if channel:
        args["channel"] = channel
    return args


def _render(url: str, *, timeout: int, collect_network: bool = False) -> tuple[str, str | None, dict[str, object]]:
    from patchright.sync_api import sync_playwright

    timeout_ms = timeout * 1000
    last_error: str | None = None
    for label, channel in (("chrome", "chrome"), ("bundled-chromium", None)):
        network_candidates: list[str] = []
        browser = None
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(**_launch_args(channel))
                context = browser.new_context(locale="ko-KR", timezone_id="Asia/Seoul")
                page = context.new_page()
                if collect_network:
                    page.on(
                        "request",
                        lambda request: (
                            network_candidates.append(request.url)
                            if NETWORK_CANDIDATE_RE.search(request.url)
                            else None
                        ),
                    )
                response = page.goto(url, wait_until="domcontentloaded", timeout=timeout_ms)
                page.wait_for_timeout(min(2000, max(250, timeout_ms // 10)))
                text = page.locator("body").inner_text(timeout=min(5000, timeout_ms))
                details: dict[str, object] = {
                    "headless": True,
                    "channel": label,
                    "http_status": response.status if response else None,
                }
                if collect_network:
                    details["network_candidates"] = network_candidates[:20]
                return text, None, details
        except Exception as exc:
            last_error = f"{label}:{type(exc).__name__}:{str(exc)[:200]}"
        finally:
            if browser is not None:
                try:
                    browser.close()
                except Exception:
                    pass
    return "", last_error or "patchright-render-failed", {"headless": True}


def run_patchright_stage(
    args: object,
    route: dict[str, object],
    attempts: list[AcquisitionAttempt],
    *,
    proof_required: bool,
    payload_for: PayloadFor,
    renderer: Callable[..., tuple[str, str | None, dict[str, object]]] = _render,
) -> dict[str, object] | None:
    started = time.monotonic()
    text, error, details = renderer(args.url, timeout=args.timeout, collect_network=False)
    attempts.append(
        attempt_from_text(
            stage_id="patchright-render-recon",
            tool_id="patchright",
            text=text,
            elapsed_s=round(time.monotonic() - started, 3),
            error=error,
            intent=args.intent,
            expect_text=args.expect_text,
            expect_regex=args.expect_regex,
            expect_json_field=args.expect_json_field,
            details=details,
        )
    )
    if args.intent == "collect":
        started = time.monotonic()
        network_text, network_error, network_details = renderer(args.url, timeout=args.timeout, collect_network=True)
        attempts.append(
            AcquisitionAttempt(
                stage_id="patchright-network-recon",
                tool_id="patchright",
                status="diagnostic" if network_error is None else "error",
                confidence="weak" if network_text.strip() else "none",
                elapsed_s=round(time.monotonic() - started, 3),
                error=network_error,
                output_chars=len(network_text),
                details={**network_details, "diagnostic": True},
            )
        )
    if has_success(attempts, proof_required=proof_required):
        return payload_for(args, route, attempts, "success")
    return None
