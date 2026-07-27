#!/usr/bin/env python3
"""Propose merge candidates from parsed handoff entries.

CLI surface:

    python3 propose_merges.py --entries <path-to-parser-json>
    python3 propose_merges.py --entries -                # read stdin

Reads the JSON payload emitted by ``parse_handoff_entries.py`` (the
``entries`` array), rebuilds the HandoffEntry list, and emits a
MergeProposal JSON on stdout (standalone candidates + merged candidates
+ shared_boundary_reason map).

See ``references/chunked-routing.md`` for the contract (in the charness source
repo the full implementation contract is ``docs/handoff-chunked-routing.md``,
which is not vendored with the skill).
"""
import argparse
import json
import runpy
import sys
from pathlib import Path
from types import SimpleNamespace


def _load_skill_runtime_bootstrap():
    bootstrap = next((ancestor / "skill_runtime_bootstrap.py" for ancestor in Path(__file__).resolve().parents if (ancestor / "skill_runtime_bootstrap.py").is_file()), None)
    if bootstrap is None:
        raise ImportError("skill_runtime_bootstrap.py not found")
    return SimpleNamespace(**runpy.run_path(str(bootstrap)))


SKILL_RUNTIME = _load_skill_runtime_bootstrap()
chunked_routing_lib = SKILL_RUNTIME.load_local_skill_module(__file__, "chunked_routing_lib")
chunked_routing_cli = SKILL_RUNTIME.load_local_skill_module(__file__, "chunked_routing_cli")


def _restore_entries(payload):
    """Accept either the full parser payload or just the entries array."""
    is_payload = isinstance(payload, dict)
    diagnostic = payload.get("issue_source_diagnostic") if is_payload else None
    staleness = payload.get("staleness") if is_payload else None
    try:
        return chunked_routing_lib.entries_from_payload(payload), diagnostic, staleness
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    chunked_routing_cli.add_input_argument(
        parser,
        legacy=("--entries",),
        help_text=(
            "A parse_handoff_entries.py payload (with entries[]) or a bare "
            "entries array. `--entries` is a kept alias."
        ),
    )
    return parser.parse_args()


def main() -> int:
    cancel_timeout = SKILL_RUNTIME.arm_cli_timeout(label="handoff propose_merges")
    try:
        args = parse_args()
        payload = chunked_routing_cli.read_pipeline_json(
            args.input,
            stage="propose_merges",
            expects="a parse_handoff_entries payload (with entries[]) or an entries array",
        )
        entries, issue_source_diagnostic, staleness = _restore_entries(payload)
        proposal = chunked_routing_lib.propose_merges(entries)
        output = proposal.to_dict()
        if issue_source_diagnostic is not None:
            output["issue_source_diagnostic"] = issue_source_diagnostic
        # Forwarded, not recomputed: the checked/not-checked flags must survive
        # to the stage that builds the agent's packet, or the per-entry facts
        # arrive stripped of the one thing that makes an empty list readable.
        if staleness is not None:
            output["staleness"] = staleness
        sys.stdout.write(json.dumps(output, ensure_ascii=False, indent=2) + "\n")
        return 0
    finally:
        cancel_timeout()


if __name__ == "__main__":
    raise SystemExit(main())
