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
import importlib.util
import json
import sys
from pathlib import Path


def _load_skill_runtime_bootstrap():
    script_path = Path(__file__).resolve()
    for ancestor in script_path.parents:
        candidate = ancestor / "skill_runtime_bootstrap.py"
        if candidate.is_file():
            spec = importlib.util.spec_from_file_location("skill_runtime_bootstrap", candidate)
            if spec is None or spec.loader is None:
                continue
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module
    raise ImportError("skill_runtime_bootstrap.py not found")


SKILL_RUNTIME = _load_skill_runtime_bootstrap()
chunked_routing_lib = SKILL_RUNTIME.load_local_skill_module(__file__, "chunked_routing_lib")
chunked_routing_cli = SKILL_RUNTIME.load_local_skill_module(__file__, "chunked_routing_cli")


def _restore_entries(payload):
    """Accept either the full parser payload or just the entries array."""
    diagnostic = None
    if isinstance(payload, dict) and "entries" in payload:
        entry_dicts = payload["entries"]
        diagnostic = payload.get("issue_source_diagnostic")
    elif isinstance(payload, list):
        entry_dicts = payload
    else:
        raise SystemExit("input JSON must be either a parser payload or an entries array")
    entries = [
        chunked_routing_lib.HandoffEntry(
            index=int(entry["index"]),
            title=entry["title"],
            body=entry["body"],
            referenced_paths=tuple(entry.get("referenced_paths", [])),
            referenced_issues=tuple(entry.get("referenced_issues", [])),
            referenced_skills=tuple(entry.get("referenced_skills", [])),
            boundary_tokens=tuple(entry.get("boundary_tokens", [])),
        )
        for entry in entry_dicts
    ]
    return entries, diagnostic


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
        entries, issue_source_diagnostic = _restore_entries(payload)
        proposal = chunked_routing_lib.propose_merges(entries)
        output = proposal.to_dict()
        if issue_source_diagnostic is not None:
            output["issue_source_diagnostic"] = issue_source_diagnostic
        sys.stdout.write(json.dumps(output, ensure_ascii=False, indent=2) + "\n")
        return 0
    finally:
        cancel_timeout()


if __name__ == "__main__":
    raise SystemExit(main())
