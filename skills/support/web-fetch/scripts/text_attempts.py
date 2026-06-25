"""Shared text-to-attempt helpers for public URL acquisition stages."""

from __future__ import annotations

from acquisition_trace_lib import AcquisitionAttempt
from classify_fetch_response import classify, extract_persistable_text


def _http_error_status(details: dict[str, object] | None) -> int | None:
    if not details:
        return None
    status = details.get("http_status")
    if isinstance(status, int) and status >= 400:
        return status
    return None


def attempt_from_text(
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
    details = details or {}
    classification = classify(
        text,
        intent=intent,
        expect_text=expect_text,
        expect_regex=expect_regex,
        expect_json_field=expect_json_field,
    )
    status = str(classification["status"])
    http_status = _http_error_status(details)
    if http_status is not None and status != "invalid-proof":
        status = "error-page"
        classification = {
            **classification,
            "status": status,
            "confidence": "none",
            "signals": [*classification.get("signals", []), "http-error"],
            "matched_signals": [*classification.get("matched_signals", []), f"http-status:{http_status}"],
            "recommended_next_step": "Treat this as a failed fetch and move to the next route.",
        }
    if error is not None and status != "invalid-proof":
        status = "error"
    return AcquisitionAttempt(
        stage_id=stage_id,
        tool_id=tool_id,
        status=status,
        confidence=str(classification.get("confidence", "none")),
        elapsed_s=elapsed_s,
        error=error,
        output_chars=len(text),
        classification=classification,
        details=details,
        content_text=extract_persistable_text(text, content_format=content_format),
        content_format=content_format,
    )
