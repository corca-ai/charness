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


# Facts the parser established that must reach the agent-facing packet unchanged.
CARRIED_KEYS = (
    "issue_source_diagnostic",
    "staleness",
    "issue_adapter_report",
    "handoff_adapter_report",
)


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
        entries = chunked_routing_cli.entries_from_pipeline_payload(
            payload, chunked_routing_lib
        )
        proposal = chunked_routing_lib.propose_merges(entries)
        output = proposal.to_dict()
        chunked_routing_cli.forward_carried_keys(payload, output, CARRIED_KEYS)
        sys.stdout.write(json.dumps(output, ensure_ascii=False, indent=2) + "\n")
        return 0
    finally:
        cancel_timeout()


if __name__ == "__main__":
    raise SystemExit(main())
