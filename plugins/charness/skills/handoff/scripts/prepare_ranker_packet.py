#!/usr/bin/env python3
"""Build the generative-sequence ranker packet handed to the agent.

CLI surface:

    python3 prepare_ranker_packet.py --merge-proposal <path-to-json>
    python3 prepare_ranker_packet.py --merge-proposal -        # read stdin

The packet is a self-contained JSON payload: the agent fills the
``ranked_chunks`` array per the embedded ``response_schema`` and the
parent calls
``chunked_routing_lib.validate_ranker_response`` on the filled payload.

See ``docs/handoff-chunked-routing.md`` for the contract.
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


def _read_merge_proposal_json(path_arg: str) -> dict:
    if path_arg == "-":
        return json.loads(sys.stdin.read())
    return json.loads(Path(path_arg).expanduser().resolve().read_text(encoding="utf-8"))


def _restore_merge_proposal(payload: dict):
    """Rebuild a MergeProposal from JSON emitted by ``MergeProposal.to_dict()``."""

    def restore_entry(entry_dict):
        return chunked_routing_lib.HandoffEntry(
            index=int(entry_dict["index"]),
            title=entry_dict["title"],
            body=entry_dict["body"],
            referenced_paths=tuple(entry_dict.get("referenced_paths", [])),
            referenced_issues=tuple(entry_dict.get("referenced_issues", [])),
            referenced_skills=tuple(entry_dict.get("referenced_skills", [])),
            boundary_tokens=tuple(entry_dict.get("boundary_tokens", [])),
        )

    def restore_candidate(candidate_dict):
        return chunked_routing_lib.ChunkCandidate(
            entries=tuple(restore_entry(entry) for entry in candidate_dict["entries"]),
            label=candidate_dict["label"],
            objective_summary=candidate_dict["objective_summary"],
        )

    return chunked_routing_lib.MergeProposal(
        standalone=tuple(restore_candidate(c) for c in payload.get("standalone", [])),
        merged=tuple(restore_candidate(c) for c in payload.get("merged", [])),
        shared_boundary_reason=dict(payload.get("shared_boundary_reason", {})),
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--merge-proposal",
        required=True,
        help=(
            "Path to a JSON file produced by `propose_merges.py` "
            "(emitted via MergeProposal.to_dict()), or `-` to read stdin."
        ),
    )
    return parser.parse_args()


def main() -> int:
    cancel_timeout = SKILL_RUNTIME.arm_cli_timeout(label="handoff prepare_ranker_packet")
    try:
        args = parse_args()
        payload = _read_merge_proposal_json(args.merge_proposal)
        merge_proposal = _restore_merge_proposal(payload)
        packet = chunked_routing_lib.build_ranker_packet(merge_proposal)
        sys.stdout.write(json.dumps(packet, ensure_ascii=False, indent=2) + "\n")
        return 0
    finally:
        cancel_timeout()


if __name__ == "__main__":
    raise SystemExit(main())
