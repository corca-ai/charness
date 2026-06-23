"""Browser-backed acquisition stages for public URL fetches."""

from __future__ import annotations

import time
from pathlib import Path
from typing import Callable

import youtube_browser_ui
from acquisition_trace_lib import AcquisitionAttempt, has_success
from agent_browser_session import (
    assert_runtime_clean,
    cleanup_orphans,
    close_session,
    run_browser_network,
    run_browser_text,
    session_name,
)
from text_attempts import attempt_from_text

RunCommand = Callable[..., tuple[str, str | None]]
PayloadFor = Callable[[object, dict[str, object], list[AcquisitionAttempt], str], dict[str, object]]


def _degraded_on_cleanup(
    *,
    cleanup_error: str | None,
    args: object,
    route: dict[str, object],
    attempts: list[AcquisitionAttempt],
    payload_for: PayloadFor,
) -> dict[str, object] | None:
    if not cleanup_error:
        return None
    last = attempts[-1]
    last.details["cleanup"] = "failed"
    last.details["cleanup_error"] = cleanup_error
    if last.error is None:
        last.status, last.confidence, last.error = "error", "none", cleanup_error
    return payload_for(args, route, attempts, "degraded")


def _close_cleanup_error(args: object, *, script_dir: Path, run_command: RunCommand) -> str | None:
    close_error = close_session(args.url, timeout=args.timeout, run_command=run_command)
    cleanup_error = cleanup_orphans(script_dir, args.repo_root, timeout=args.timeout, run_command=run_command)
    assert_error = None
    if cleanup_error is None:
        assert_error = assert_runtime_clean(script_dir, args.repo_root, timeout=args.timeout, run_command=run_command)
    return close_error or cleanup_error or assert_error


def _finish_stage(
    args: object,
    route: dict[str, object],
    attempts: list[AcquisitionAttempt],
    *,
    cleanup_error: str | None,
    proof_required: bool,
    payload_for: PayloadFor,
) -> dict[str, object] | None:
    degraded = _degraded_on_cleanup(
        cleanup_error=cleanup_error, args=args, route=route, attempts=attempts, payload_for=payload_for
    )
    if degraded is not None:
        return degraded
    if has_success(attempts, proof_required=proof_required):
        return payload_for(args, route, attempts, "success")
    return None


def run_generic_browser_stage(
    args: object,
    route: dict[str, object],
    attempts: list[AcquisitionAttempt],
    *,
    proof_required: bool,
    script_dir: Path,
    run_command: RunCommand,
    payload_for: PayloadFor,
) -> dict[str, object] | None:
    cleanup_error = None
    try:
        started = time.monotonic()
        text, error, details = run_browser_text(args.url, timeout=args.timeout, run_command=run_command)
        attempts.append(
            attempt_from_text(
                stage_id="agent-browser-render-recon",
                tool_id="agent-browser",
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
            network_text, network_error, network_details = run_browser_network(
                args.url, timeout=args.timeout, run_command=run_command
            )
            attempts.append(
                AcquisitionAttempt(
                    stage_id="agent-browser-network-recon",
                    tool_id="agent-browser",
                    status="diagnostic" if network_error is None else "error",
                    confidence="weak" if network_text.strip() else "none",
                    elapsed_s=round(time.monotonic() - started, 3),
                    error=network_error,
                    output_chars=len(network_text),
                    details={**network_details, "diagnostic": True},
                )
            )
    finally:
        cleanup_error = _close_cleanup_error(args, script_dir=script_dir, run_command=run_command)
    return _finish_stage(
        args, route, attempts,
        cleanup_error=cleanup_error, proof_required=proof_required, payload_for=payload_for,
    )


def run_youtube_browser_stage(
    args: object,
    route: dict[str, object],
    attempts: list[AcquisitionAttempt],
    *,
    proof_required: bool,
    script_dir: Path,
    run_command: RunCommand,
    payload_for: PayloadFor,
) -> dict[str, object] | None:
    cleanup_error = None
    try:
        attempts.append(
            youtube_browser_ui.run_browser_ui_transcript_stage(
                args.url,
                session=session_name(args.url),
                run_command=lambda command: run_command(command, timeout=args.timeout),
            )
        )
    finally:
        cleanup_error = _close_cleanup_error(args, script_dir=script_dir, run_command=run_command)
    return _finish_stage(
        args, route, attempts,
        cleanup_error=cleanup_error, proof_required=proof_required, payload_for=payload_for,
    )
