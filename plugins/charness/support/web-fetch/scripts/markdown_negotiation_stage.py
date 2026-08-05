from __future__ import annotations

import time
from argparse import Namespace
from collections.abc import Callable
from urllib.parse import urlparse

from acquisition_trace_lib import AcquisitionAttempt, has_stage, has_success, skip_attempt
from text_attempts import attempt_from_text


def _markdown_looking_url(url: str) -> bool:
    path = urlparse(url).path.lower()
    return path.endswith((".md", ".markdown"))


def try_stage(
    args: Namespace,
    route: dict[str, object],
    attempts: list[AcquisitionAttempt],
    direct_attempt: AcquisitionAttempt,
    *,
    proof_required: bool,
    read_direct: Callable[..., tuple[str, str | None]],
    markdown_accept: str,
    payload_for: Callable[..., dict[str, object]],
) -> dict[str, object] | None:
    eligible = direct_attempt.status == "login-wall" or _markdown_looking_url(args.url)
    if not eligible:
        return None
    if args.direct_response_file is not None:
        if has_stage(route, "content-negotiated-markdown"):
            attempts.append(skip_attempt("content-negotiated-markdown", None, reason="seeded-direct-fixture"))
        return None
    started = time.monotonic()
    text, error = read_direct(
        args.url,
        timeout=args.timeout,
        direct_response_file=None,
        accept=markdown_accept,
    )
    attempts.append(
        attempt_from_text(
            stage_id="content-negotiated-markdown",
            tool_id=None,
            text=text,
            elapsed_s=round(time.monotonic() - started, 3),
            error=error,
            intent=args.intent,
            expect_text=args.expect_text,
            expect_regex=args.expect_regex,
            expect_json_field=args.expect_json_field,
            details={
                "accept": markdown_accept,
                "representation": "markdown",
                "route": "content-negotiated-markdown",
                "trigger": "direct-login-wall" if direct_attempt.status == "login-wall" else "markdown-looking-url",
            },
            content_format="markdown",
        )
    )
    if has_success(attempts, proof_required=proof_required):
        return payload_for(args, route, attempts, "success")
    return None
