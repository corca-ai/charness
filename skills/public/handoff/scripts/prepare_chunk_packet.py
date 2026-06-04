#!/usr/bin/env python3
"""Build the agentic work-package packet for handoff chunked routing.

Consumes the parser payload emitted by ``parse_handoff_entries.py`` or a bare
``entries`` array. Emits sources, overlap hints, adapter policy, prompt, and
response schema for the agentic package proposal stage.
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
    if isinstance(payload, dict) and "entries" in payload:
        entry_dicts = payload["entries"]
    elif isinstance(payload, list):
        entry_dicts = payload
    else:
        raise SystemExit("input JSON must be either a parser payload or an entries array")
    return [
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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path.cwd(),
        help="Repo root used to read optional handoff chunk policy.",
    )
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
    cancel_timeout = SKILL_RUNTIME.arm_cli_timeout(label="handoff prepare_chunk_packet")
    try:
        args = parse_args()
        payload = chunked_routing_cli.read_pipeline_json(
            args.input,
            stage="prepare_chunk_packet",
            expects="a parse_handoff_entries payload (with entries[]) or an entries array",
        )
        entries = _restore_entries(payload)
        hints = chunked_routing_lib.propose_merges(entries)
        policy = chunked_routing_lib.load_chunk_policy_config(args.repo_root.resolve())
        packet = chunked_routing_lib.build_chunk_proposal_packet(
            entries,
            merge_proposal=hints,
            policy=policy,
        )
        sys.stdout.write(json.dumps(packet, ensure_ascii=False, indent=2) + "\n")
        return 0
    finally:
        cancel_timeout()


if __name__ == "__main__":
    raise SystemExit(main())
