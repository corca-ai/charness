#!/usr/bin/env python3
"""Build the generative-sequence ranker packet handed to the agent.

CLI surface:

    python3 prepare_ranker_packet.py --merge-proposal <path-to-json>
    python3 prepare_ranker_packet.py --merge-proposal -        # read stdin

The packet is a self-contained JSON payload: the agent fills the
``ranked_chunks`` array per the embedded ``response_schema`` and the
parent calls
``chunked_routing_lib.validate_ranker_response`` on the filled payload.

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
            judgment_summary=candidate_dict.get("judgment_summary"),
        )

    return chunked_routing_lib.MergeProposal(
        standalone=tuple(restore_candidate(c) for c in payload.get("standalone", [])),
        merged=tuple(restore_candidate(c) for c in payload.get("merged", [])),
        shared_boundary_reason=dict(payload.get("shared_boundary_reason", {})),
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    chunked_routing_cli.add_input_argument(
        parser,
        legacy=("--merge-proposal",),
        help_text=(
            "A MergeProposal JSON from propose_merges.py "
            "(MergeProposal.to_dict()). `--merge-proposal` is a kept alias."
        ),
    )
    return parser.parse_args()


def main() -> int:
    cancel_timeout = SKILL_RUNTIME.arm_cli_timeout(label="handoff prepare_ranker_packet")
    try:
        args = parse_args()
        payload = chunked_routing_cli.read_pipeline_json(
            args.input,
            stage="prepare_ranker_packet",
            expects="a MergeProposal JSON from propose_merges.py",
        )
        merge_proposal = _restore_merge_proposal(payload)
        packet = chunked_routing_lib.build_ranker_packet(merge_proposal)
        sys.stdout.write(json.dumps(packet, ensure_ascii=False, indent=2) + "\n")
        return 0
    finally:
        cancel_timeout()


if __name__ == "__main__":
    raise SystemExit(main())
