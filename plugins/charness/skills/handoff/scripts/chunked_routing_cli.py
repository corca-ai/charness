#!/usr/bin/env python3
"""Shared CLI input convention for the handoff chunker pipeline stages.

# Every JSON-consuming stage (``propose_merges`` -> ``prepare_chunk_packet``
-> ``prepare_ranker_packet`` -> ``draft_goal_from_chunk``) exposes one predictable input flag —
``--input``/``-i`` plus its legacy stage-specific alias — defaulting to ``-``
(stdin), so ``parse | propose | chunk-packet | prepare`` composes without a temp file or a
per-stage ``--help`` round-trip.

It also makes a malformed input fail **loudly at the stage that read it**: a
structured error on stderr + exit 2 naming the stage and the expected input,
instead of letting a wrong upstream ``--flag`` (whose argparse usage text was
redirected into the file) masquerade as an opaque ``JSONDecodeError`` two
stages downstream.

This is intentionally a tiny standalone module, not an addition to
``chunked_routing_lib.py`` (held under its size budget per recent-lessons).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


def add_input_argument(
    parser: argparse.ArgumentParser,
    *,
    legacy: tuple[str, ...] = (),
    help_text: str | None = None,
) -> None:
    """Add the uniform ``--input``/``-i`` JSON input flag to ``parser``.

    ``legacy`` carries the stage's prior flag name(s) (e.g. ``--entries``) as
    aliases so existing callers and tests keep working. The input defaults to
    ``-`` (stdin) so the pipeline composes as a plain pipe.
    """
    flags = ["--input", "-i", *legacy]
    suffix = f" {help_text}" if help_text else ""
    parser.add_argument(
        *flags,
        dest="input",
        default="-",
        help=(
            "JSON input path, or '-' for stdin (default: stdin)." + suffix
        ),
    )


def read_pipeline_json(input_arg: str, *, stage: str, expects: str) -> Any:
    """Read and parse JSON from ``input_arg`` ('-' = stdin), failing loudly.

    On a missing file or invalid JSON, emit a structured error to stderr that
    names the reading ``stage`` and the ``expects`` shape, then exit 2 — so the
    failure surfaces at its cause, not as a cryptic JSON error downstream.
    """
    if input_arg == "-":
        raw = sys.stdin.read()
        source = "<stdin>"
    else:
        path = Path(input_arg).expanduser()
        if not path.is_file():
            _fail(stage=stage, source=str(path), expects=expects,
                  reason="input file not found")
        raw = path.read_text(encoding="utf-8")
        source = str(path)
    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        _fail(
            stage=stage,
            source=source,
            expects=expects,
            reason=f"input is not valid JSON ({exc})",
            hint=(
                "a wrong upstream --flag may have written argparse usage text "
                "into this input; check the previous stage's invocation"
            ),
        )


def _fail(*, stage: str, source: str, expects: str, reason: str,
          hint: str | None = None) -> "None":
    payload = {
        "ok": False,
        "stage": stage,
        "source": source,
        "expects": expects,
        "error": reason,
    }
    if hint:
        payload["hint"] = hint
    print(json.dumps(payload, ensure_ascii=False), file=sys.stderr)
    raise SystemExit(2)
