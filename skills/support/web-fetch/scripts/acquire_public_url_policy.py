from __future__ import annotations

import shutil

import youtube_source
from acquisition_trace_lib import AcquisitionAttempt, last_content_attempt, should_stop


def should_try_defuddle(route_id: str, attempts: list[AcquisitionAttempt]) -> tuple[bool, str | None]:
    if route_id not in {"direct-then-fallback", "reader-fallback", "naver-blog-mobile"}:
        return False, "route-not-applicable"
    last = last_content_attempt(attempts)
    if last is not None and last.status not in {"partial-content", "empty-spa", "unclear", "error", "captcha", "error-page"}:
        return False, "prior-stage-sufficient"
    if shutil.which("defuddle") is None:
        return False, "missing-tool"
    return True, None


def should_try_browser(
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


def should_try_youtube_browser(
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


def direct_attempt_sufficient(
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
