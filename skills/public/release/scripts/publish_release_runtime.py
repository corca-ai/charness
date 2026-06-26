from __future__ import annotations

import json
import sys
import time
from typing import Any, Callable, TextIO, TypeVar

T = TypeVar("T")


def record_runtime(payload: dict[str, Any], label: str, start: float) -> None:
    payload.setdefault("release_runtime", []).append(
        {"label": label, "elapsed_seconds": round(time.perf_counter() - start, 3)}
    )


def timed(payload: dict[str, Any], label: str, callback: Callable[[], T]) -> T:
    start = time.perf_counter()
    try:
        return callback()
    finally:
        record_runtime(payload, label, start)


def print_failure_payload(
    payload: dict[str, Any],
    error: BaseException,
    *,
    stream: TextIO = sys.stderr,
) -> None:
    visible_keys = (
        "package_id",
        "previous_version",
        "target_version",
        "tag_name",
        "remote",
        "branch",
        "expected_release_url",
        "fresh_checkout_probe_status",
        "public_release_verification",
        "release_runtime",
    )
    failure_payload = {key: payload[key] for key in visible_keys if key in payload}
    failure_payload["release_failure"] = {"status": "failed", "error": str(error)}
    print("BEGIN publish_release_failure_payload", file=stream)
    print(json.dumps(failure_payload, ensure_ascii=False, indent=2), file=stream)
    print("END publish_release_failure_payload", file=stream)
