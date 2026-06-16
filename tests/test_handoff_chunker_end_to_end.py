"""Slice 7 end-to-end pipeline test.

Feeds the 2026-05-28 handoff snapshot through the full chain:

    parse_handoff_entries
      -> propose_merges (deterministic hints)
        -> prepare_chunk_packet
          -> validate/materialize known-good package response
            -> prepare_ranker_packet
              -> consume known-good ranking
                -> draft_goal_from_chunk
                  -> check_goal_artifact.check_goal (ok at status draft)

Asserts the auto-drafted goal artifact passes check_goal_artifact and
carries the right standalone-vs-merged shape, single-prefix heading,
and placeholder-only sections per slice-5's contract.

This is the closeout-stage proof that the pipeline composes end-to-end,
not just slice-by-slice.
"""
from __future__ import annotations

import importlib.util
import json
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
FIXTURE_PATH = REPO_ROOT / "tests" / "fixtures" / "handoff-snapshot-2026-05-28.md"
LIB_PATH = (
    REPO_ROOT
    / "skills"
    / "public"
    / "handoff"
    / "scripts"
    / "chunked_routing_lib.py"
)
GOAL_LIB_PATH = (
    REPO_ROOT
    / "skills"
    / "public"
    / "achieve"
    / "scripts"
    / "goal_artifact_lib.py"
)
DRAFTER_SCRIPT = (
    REPO_ROOT
    / "skills"
    / "public"
    / "handoff"
    / "scripts"
    / "draft_goal_from_chunk.py"
)


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def lib():
    return _load(LIB_PATH, "chunked_routing_lib")


@pytest.fixture(scope="module")
def goal_lib():
    return _load(GOAL_LIB_PATH, "achieve_goal_artifact_lib")


def test_end_to_end_pipeline_produces_valid_goal_artifact(
    lib, goal_lib, tmp_path
):
    """Full chain on the real fixture: parse -> merge hints -> agentic
    packages -> ranker packet -> ranking -> draft selected chunk -> check_goal."""
    handoff_text = FIXTURE_PATH.read_text(encoding="utf-8")

    # Step 1: parse.
    entries = lib.parse_handoff_entries(handoff_text)
    assert len(entries) == 7

    # Step 2: prepare deterministic merge hints.
    hints = lib.propose_merges(entries)
    assert len(hints.standalone) == 7
    # The real fixture has no merge candidates (slice-2 negative-merge
    # invariant); the e2e proof still runs because the ranker handles
    # any merge count.
    assert len(hints.all_candidates()) == 7

    # Step 3: build and fill agentic package packet.
    chunk_packet = lib.build_chunk_proposal_packet(entries, merge_proposal=hints)
    assert chunk_packet["version"] == lib.CHUNK_PROPOSAL_PACKET_VERSION
    package_response = {
        "chunks": [
            {
                "label": f"fixture-entry-{entry.index}",
                "source_ids": [entry.index],
                "objective_summary": entry.title,
                "rationale": "Standalone package: no honest fixture merge exists.",
                "downstream_unlock": "Keeps the fixture's negative-merge invariant explicit.",
                "judgment_summary": {
                    "semantic_fit": "Single fixture entry is the only honest semantic fit.",
                    "implementation_boundary": "The fixture entry stands on its own boundary.",
                    "closeout_flow": "The fixture entry can be verified independently.",
                    "operator_value": "Keeping it standalone preserves the negative-merge signal.",
                },
                "excluded_source_ids": [
                    other.index for other in entries if other.index != entry.index
                ],
                "basis_boundary_tokens": [],
            }
            for entry in entries
        ]
    }
    validation = lib.validate_chunk_proposal_response(package_response, entries)
    assert validation["ok"] is True, validation["issues"]
    proposal = lib.materialize_chunk_proposal_response(package_response, entries)
    candidates = proposal.all_candidates()
    assert len(candidates) == 7

    # Step 4: build ranker packet.
    packet = lib.build_ranker_packet(proposal)
    assert packet["version"] == lib.RANKER_PACKET_VERSION
    assert packet["ranker_prompt"] == lib.RANKER_PROMPT

    # Step 4.5: simulate the agent filling the packet. The reasoning is
    # written in the generative-sequence shape the prompt requires (names
    # the unlock relation, not a restatement of objective_summary).
    labels = [candidate.label for candidate in candidates]
    response = {
        "ranked_chunks": [
            {
                "candidate_label": candidate.label,
                "rank": index + 1,
                "reasoning": (
                    f"Resolving this chunk first removes the uncertainty "
                    f"that chunk `{labels[index + 1]}` would otherwise "
                    f"hit during its verification path."
                )
                if index < len(labels) - 1
                else (
                    "Comes last because every earlier chunk has already "
                    "removed the uncertainty this one would depend on."
                ),
            }
            for index, candidate in enumerate(candidates)
        ]
    }

    # Step 4.9: validate the simulated response.
    validation = lib.validate_ranker_response(response, proposal)
    assert validation["ok"] is True, validation["issues"]

    # Step 5: materialize ranked chunks.
    ranked = lib.parse_ranked_chunks(response, proposal)
    assert len(ranked) == 7
    for chunk in ranked:
        # Slice-3 why-not follow-up contract: every chunk carries
        # non-empty reasoning so the agent can answer "why not chunk N?"
        # without re-running the ranker.
        assert chunk.reasoning

    # Step 6: pick a chunk (the first ranked one) and draft.
    selected = ranked[0].candidate
    chunk_payload = json.dumps(selected.to_dict())
    result = subprocess.run(
        [
            "python3",
            str(DRAFTER_SCRIPT),
            "--chunk",
            "-",
            "--date",
            "2026-05-28",
            "--slug",
            "e2e-smoke",
            "--repo-root",
            str(tmp_path),
        ],
        input=chunk_payload,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["ok"] is True
    assert payload["status"] == "draft"
    artifact_path = Path(payload["path"])
    assert artifact_path.is_file()

    # Step 6: confirm check_goal accepts the drafted artifact.
    text = artifact_path.read_text(encoding="utf-8")
    report = goal_lib.check_goal(text)
    assert report["ok"] is True, report["issues"]
    assert report["status"] == "draft"

    # And the slice-5 single-prefix heading invariant survives the e2e
    # round-trip too.
    assert text.splitlines()[0].startswith("# Achieve Goal: ")
    assert "Achieve Goal: Achieve Goal:" not in text


def test_end_to_end_trigger_then_pipeline_matches_user_flow(lib):
    """Slice-7 e2e: when the user says one of the trigger-fixture
    chunk-cases, the chunker fires and produces a candidate list. When
    the user says a no-chunk case, the chunker steps aside.

    Pins the integration between trigger detection (slice 7 trigger
    test) and the pipeline (this test); a regression that left the
    trigger correct but broke the pipeline would still fail this
    integration."""
    handoff_text = FIXTURE_PATH.read_text(encoding="utf-8")
    chunk_messages = (
        "read docs/handoff.md",
        "what's next in the handoff?",
        "핸드오프 봐",
        "pick up from handoff",
    )
    no_chunk_messages = (
        "read handoff and start slice 7",
        "push the slice 7 commits",
        "read handoff.md and fix #233",
    )
    entries = lib.parse_handoff_entries(handoff_text)
    response = {
        "chunks": [
            {
                "label": f"trigger-entry-{entry.index}",
                "source_ids": [entry.index],
                "objective_summary": entry.title,
                "rationale": "Trigger smoke keeps each fixture source standalone.",
                "downstream_unlock": "Proves the chunker reaches package candidates.",
                "judgment_summary": {
                    "semantic_fit": "The trigger smoke source is self-contained.",
                    "implementation_boundary": "The smoke source has one handoff trigger boundary.",
                    "closeout_flow": "The smoke source can be validated in this fixture path.",
                    "operator_value": "Standalone output keeps the pickup signal legible.",
                },
                "basis_boundary_tokens": [],
            }
            for entry in entries
        ]
    }
    assert lib.validate_chunk_proposal_response(response, entries)["ok"] is True
    proposal = lib.materialize_chunk_proposal_response(response, entries)
    for message in chunk_messages:
        assert lib.should_fire_chunker(message) is True
        # When the chunker fires, the pipeline reaches a non-empty
        # candidate list. The candidate list IS the offer made to the
        # user; an empty list here would be a silent regression.
        assert len(proposal.all_candidates()) > 0
    for message in no_chunk_messages:
        assert lib.should_fire_chunker(message) is False
