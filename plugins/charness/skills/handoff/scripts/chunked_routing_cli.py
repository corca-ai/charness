#!/usr/bin/env python3
"""Shared CLI input convention for the handoff chunker pipeline stages.

# Every payload-consuming stage (``propose_merges`` -> ``prepare_chunk_packet``
-> ``prepare_ranker_packet`` -> ``draft_goal_from_chunk``) exposes one predictable input flag —
``--input``/``-i`` — defaulting to ``-``
(stdin), so ``parse | propose | chunk-packet | prepare`` composes without a temp file or a
per-stage ``--help`` round-trip.

It also makes a malformed input fail **loudly at the stage that read it**: a
structured error on stderr + exit 2 naming the stage and the expected input,
instead of letting a wrong upstream ``--flag`` (whose argparse usage text was
redirected into the file) masquerade as an opaque parse error two
stages downstream.

This is intentionally a tiny standalone module, not an addition to
``chunked_routing_lib.py`` (held under its size budget per recent-lessons).
"""
from __future__ import annotations

import argparse
import json
import runpy
import sys
from pathlib import Path
from typing import Any


def _load_yaml_output():
    """Reach the repo-level YAML emitter from BOTH the authoring and installed layouts.

    This module is loaded as a plain sibling by every pipeline stage rather than
    through ``skill_runtime_bootstrap``, so the ancestor walk is the one spelling
    that finds ``scripts/yaml_output.py`` at the repo root here and at the plugin
    root once exported.
    """
    helper = next(
        (
            ancestor / "scripts" / "yaml_output.py"
            for ancestor in Path(__file__).resolve().parents
            if (ancestor / "scripts" / "yaml_output.py").is_file()
        ),
        None,
    )
    if helper is None:
        raise ImportError("scripts/yaml_output.py not found")
    return runpy.run_path(str(helper))


render_yaml = _load_yaml_output()["render_yaml"]


def add_input_argument(
    parser: argparse.ArgumentParser,
    *,
    help_text: str | None = None,
) -> None:
    """Add the uniform ``--input``/``-i`` payload input flag to ``parser``.

    The input defaults to ``-`` (stdin) so the pipeline composes as a plain pipe.
    """
    suffix = f" {help_text}" if help_text else ""
    parser.add_argument(
        "--input",
        "-i",
        dest="input",
        default="-",
        help=(
            "YAML (or JSON) input path, or '-' for stdin (default: stdin)." + suffix
        ),
    )


def read_pipeline_json(input_arg: str, *, stage: str, expects: str) -> Any:
    """Read and parse the stage payload from ``input_arg`` ('-' = stdin), failing loudly.

    JSON is tried first and YAML second, in that order deliberately. Every repo-owned
    STAGE now emits YAML, so the JSON arm exists for one remaining producer: an
    AGENT-AUTHORED filled packet, which the agent writes as JSON. A parser that read
    only one of the two would break the pipeline at that seam. JSON is a YAML subset,
    so trying it first is only a fast path that keeps this readable without PyYAML
    installed.

    On a missing file or an unparseable payload, emit a structured error to stderr
    that names the reading ``stage`` and the ``expects`` shape, then exit 2 — so the
    failure surfaces at its cause, not as a cryptic parse error downstream.
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
        # Bound to a local, because Python unbinds the `except` name at block exit
        # and the YAML fallback below still has to name why JSON was rejected.
        json_error = str(exc)
    try:
        import yaml
    except ImportError:
        _fail(
            stage=stage,
            source=source,
            expects=expects,
            reason=f"input is not valid JSON ({json_error}) and PyYAML is not importable "
            f"by this interpreter ({sys.executable}) to read it as YAML",
        )
    # Refuse argparse leakage BEFORE the YAML fallback can launder it. This guard reads
    # the RAW TEXT rather than the parsed result on purpose: `usage: prog [-h]` followed
    # by `prog: error: ...` is not valid JSON, but it IS a valid YAML mapping, so adding
    # the YAML fallback quietly turned a loud upstream failure into a readable payload.
    # Measured: `prepare_ranker_packet.py` exited 0 and emitted a complete packet with
    # empty `standalone`/`merged` — a wrong upstream `--flag` producing a plausible
    # empty result instead of an error. `usage:` is argparse's own first token and no
    # pipeline payload starts with it, so the discrimination is exact.
    if raw.lstrip().startswith("usage:"):
        _fail(
            stage=stage,
            source=source,
            expects=expects,
            reason="input is argparse usage text, not a stage payload",
            hint=(
                "a wrong upstream --flag wrote argparse usage text into this input; "
                "check the previous stage's invocation"
            ),
        )
    try:
        payload = yaml.safe_load(raw)
    except yaml.YAMLError as exc:
        _fail(
            stage=stage,
            source=source,
            expects=expects,
            reason=f"input is not valid YAML or JSON ({exc})",
            hint=(
                "a wrong upstream --flag may have written argparse usage text "
                "into this input; check the previous stage's invocation"
            ),
        )
    # Structural refusal, because a prefix denylist only ever fixes the contaminant
    # someone already noticed. Empty stdin (the normal shape when an upstream stage
    # exits 2 and writes nothing) parses to None, and any stray line parses to a
    # scalar; both then reached `payload.get(...)` and died with an
    # `AttributeError: 'NoneType' object has no attribute 'get'` traceback -- the exact
    # opposite of the "structured error on stderr + exit 2 naming the stage" this
    # module's docstring promises.
    if payload is None or not isinstance(payload, (dict, list)):
        _fail(
            stage=stage,
            source=source,
            expects=expects,
            reason=(
                "input is empty" if payload is None
                else f"input parsed as a bare {type(payload).__name__}, not a payload"
            ),
            hint=(
                "an upstream stage that refused writes nothing to stdout; check its "
                "exit code rather than piping its (empty) output onward"
            ),
        )
    # A stage REFUSAL is not a stage payload. `_fail` and `stage_refusal` both emit a
    # valid YAML mapping now, so redirecting a failing stage's stderr into the next
    # stage hands it something that parses perfectly and carries none of the fields it
    # reads. Refusing it here is what keeps a failed pipeline from producing a
    # plausible EMPTY result instead of an error.
    if isinstance(payload, dict) and payload.get("ok") is False and "stage" in payload:
        _fail(
            stage=stage,
            source=source,
            expects=expects,
            reason=(
                f"input is a refusal payload from stage `{payload.get('stage')}`, "
                "not a stage payload"
            ),
            hint=(
                "the upstream stage refused; its stderr was captured as this stage's "
                "input. Fix the upstream failure rather than forwarding its refusal"
            ),
        )
    return payload


def entries_from_pipeline_payload(payload: Any, chunked_routing_lib: Any) -> Any:
    """Accept either the full parser payload or a bare entries array.

    Shared by ``propose_merges`` and ``prepare_chunk_packet``: both restore the
    same records from the same two input shapes, and a malformed payload must
    refuse at the stage that read it rather than surface as a traceback.
    """
    try:
        return chunked_routing_lib.entries_from_payload(payload)
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc


def forward_carried_keys(payload: Any, output: dict[str, Any], keys: tuple[str, ...]) -> None:
    """Copy each present, non-None ``keys`` entry from ``payload`` into ``output``.

    Forwarded, not recomputed. A fact the parser established must survive to the
    stage that builds the agent's packet, or it arrives stripped from the only
    surface an agent reads -- the defect recorded as F3 for
    ``issue_source_diagnostic``, and the same one ``staleness`` and
    ``issue_adapter_report`` would hit stage by stage. Absent stays absent, so a
    missing key never reads as "the check ran and found nothing".
    """
    if not isinstance(payload, dict):
        return
    for key in keys:
        value = payload.get(key)
        if value is not None:
            output[key] = value


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
    print(render_yaml(payload), end="", file=sys.stderr)
    raise SystemExit(2)


def stage_refusal(payload: dict, *, code: int = 1) -> int:
    """Emit a pipeline stage's typed refusal on stderr and RETURN its exit code.

    Sibling to `_fail`, which raises `SystemExit(2)` for a contaminated INPUT. This one
    returns instead, because a stage's own refusals are decided inside `main()` where a
    `SystemExit` would bypass the `finally` that cancels the CLI timeout — and they are
    a different verdict from "your input was not what this stage reads", so they keep a
    different code.

    `ok: False` is set here rather than trusted from the caller: every stage refusal
    carries it, and a payload that omitted it would read as a success to any consumer
    keying on that field.
    """
    print(render_yaml({**payload, "ok": False}), end="", file=sys.stderr)
    return code
