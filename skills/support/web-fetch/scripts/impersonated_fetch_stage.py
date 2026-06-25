"""curl_cffi-backed public fetch stage."""

from __future__ import annotations

import importlib.util
import time
from typing import Callable

from acquisition_trace_lib import AcquisitionAttempt, has_success
from text_attempts import attempt_from_text

PayloadFor = Callable[[object, dict[str, object], list[AcquisitionAttempt], str], dict[str, object]]

IMPERSONATION_PROFILES = ("chrome120", "chrome", "safari", "firefox")


def is_available() -> bool:
    return importlib.util.find_spec("curl_cffi") is not None


def _fetch(url: str, *, timeout: int, impersonate: str) -> tuple[str, str | None, dict[str, object]]:
    from curl_cffi import requests

    response = requests.get(url, impersonate=impersonate, timeout=timeout)
    details: dict[str, object] = {
        "impersonate": impersonate,
        "http_status": response.status_code,
        "effective_url": response.url,
    }
    return response.text or "", None, details


def run_impersonated_fetch_stage(
    args: object,
    route: dict[str, object],
    attempts: list[AcquisitionAttempt],
    *,
    proof_required: bool,
    payload_for: PayloadFor,
    fetcher: Callable[..., tuple[str, str | None, dict[str, object]]] = _fetch,
) -> dict[str, object] | None:
    for profile in IMPERSONATION_PROFILES:
        started = time.monotonic()
        try:
            text, error, details = fetcher(args.url, timeout=args.timeout, impersonate=profile)
        except Exception as exc:
            text, error, details = "", f"{type(exc).__name__}:{str(exc)[:200]}", {"impersonate": profile}
        attempts.append(
            attempt_from_text(
                stage_id="impersonated-public-fetch",
                tool_id="curl_cffi",
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
        if has_success(attempts, proof_required=proof_required):
            return payload_for(args, route, attempts, "success")
    return None
