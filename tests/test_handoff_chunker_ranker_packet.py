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
PACKET_SCRIPT = (
    REPO_ROOT
    / "skills"
    / "public"
    / "handoff"
    / "scripts"
    / "prepare_ranker_packet.py"
)


def _load_lib():
    spec = importlib.util.spec_from_file_location("chunked_routing_lib", LIB_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def lib():
    return _load_lib()


@pytest.fixture(scope="module")
def merge_proposal(lib):
    """Synthesize a MergeProposal from the parsed handoff fixture.

    Slice 4 will own the real propose-merges algorithm. For slice 3 we
    only need a MergeProposal-shaped input: one standalone candidate per
    entry plus one synthetic merged candidate so the validator's
    contiguous-ranking and label-uniqueness logic both get exercised.
    """
    text = FIXTURE_PATH.read_text(encoding="utf-8")
    entries = lib.parse_handoff_entries(text)
    standalone = tuple(
        lib.ChunkCandidate(
            entries=(entry,),
            label=f"chunk-{entry.index}-{entry.title.lower().replace(' ', '-')[:20]}",
            objective_summary=entry.title,
        )
        for entry in entries
    )
    merged = (
        lib.ChunkCandidate(
            entries=(entries[1], entries[6]),  # entries 2 and 7
            label="chunk-merge-2-7-test-fixture",
            objective_summary="Synthetic merge fixture for slice 3 ranker tests.",
        ),
    )
    return lib.MergeProposal(
        standalone=standalone,
        merged=merged,
        shared_boundary_reason={
            "chunk-merge-2-7-test-fixture": "synthetic slice-3 fixture only"
        },
    )


# Packet shape ---------------------------------------------------------------


def test_packet_has_pinned_version_field(lib, merge_proposal):
    packet = lib.build_ranker_packet(merge_proposal)
    assert packet["version"] == lib.RANKER_PACKET_VERSION


def test_packet_carries_merge_proposal_round_trip(lib, merge_proposal):
    packet = lib.build_ranker_packet(merge_proposal)
    assert packet["merge_proposal"] == merge_proposal.to_dict()


def test_packet_carries_canonical_ranker_prompt(lib, merge_proposal):
    packet = lib.build_ranker_packet(merge_proposal)
    assert packet["ranker_prompt"] == lib.RANKER_PROMPT
    # The prompt must mention the generative-sequence idiom, the non-empty
    # reasoning requirement (the why-not follow-up contract), AND the
    # explicit negation of cheapest-first / input-order / alphabetical.
    # These phrase anchors catch within-prompt drift that the equality
    # assertion above cannot (because both sides would change together).
    prompt_lower = packet["ranker_prompt"].lower()
    assert "generative sequence" in prompt_lower
    assert "why not chunk" in prompt_lower
    assert "cheapest-first" in prompt_lower
    assert "alphabetical" in prompt_lower
    assert "input order" in prompt_lower


def test_packet_response_schema_requires_three_fields(lib, merge_proposal):
    packet = lib.build_ranker_packet(merge_proposal)
    schema = packet["response_schema"]
    assert schema["type"] == "object"
    chunk_schema = schema["properties"]["ranked_chunks"]["items"]
    assert set(chunk_schema["required"]) == {"candidate_label", "rank", "reasoning"}


# Response validation --------------------------------------------------------


def _filled_response(merge_proposal) -> dict:
    """A known-good filled response covering every candidate exactly once.

    The reasoning text deliberately models generative-sequence shape — it
    names the *unlock* relation to a downstream chunk rather than
    restating the chunk's own objective_summary, since RANKER_PROMPT
    explicitly forbids the latter. Future fixtures must follow the same
    pattern so the test data does not train the anti-pattern the prompt
    warns against.
    """
    candidates = merge_proposal.all_candidates()
    labels = [candidate.label for candidate in candidates]
    return {
        "ranked_chunks": [
            {
                "candidate_label": candidate.label,
                "rank": index + 1,
                "reasoning": (
                    f"Comes at position {index + 1} because resolving its "
                    f"open contract removes schema uncertainty that the "
                    f"remaining {len(labels) - index - 1} chunks "
                    f"({', '.join(labels[index + 1:]) or 'none'}) would "
                    f"otherwise rediscover."
                )
                if index < len(labels) - 1
                else (
                    "Comes last because every earlier chunk has already "
                    "removed the uncertainty this one would otherwise "
                    "depend on; safe to defer without blocking the run."
                ),
            }
            for index, candidate in enumerate(candidates)
        ]
    }


def test_validate_accepts_well_formed_response(lib, merge_proposal):
    report = lib.validate_ranker_response(
        _filled_response(merge_proposal), merge_proposal
    )
    assert report["ok"] is True, report["issues"]
    assert report["issues"] == []


def test_validate_rejects_missing_ranked_chunks(lib, merge_proposal):
    report = lib.validate_ranker_response({}, merge_proposal)
    assert report["ok"] is False
    assert any("ranked_chunks" in issue for issue in report["issues"])


def test_validate_rejects_duplicate_label(lib, merge_proposal):
    response = _filled_response(merge_proposal)
    response["ranked_chunks"][1]["candidate_label"] = response["ranked_chunks"][0][
        "candidate_label"
    ]
    report = lib.validate_ranker_response(response, merge_proposal)
    assert report["ok"] is False
    assert any("duplicate" in issue for issue in report["issues"])


def test_validate_rejects_unknown_label(lib, merge_proposal):
    response = _filled_response(merge_proposal)
    response["ranked_chunks"][0]["candidate_label"] = "nonexistent-chunk-label"
    report = lib.validate_ranker_response(response, merge_proposal)
    assert report["ok"] is False
    assert any("unknown candidate_label" in issue for issue in report["issues"])


def test_validate_rejects_non_contiguous_ranks(lib, merge_proposal):
    response = _filled_response(merge_proposal)
    # Drop the rank 1 entry, push everything else up, leaving a gap.
    response["ranked_chunks"][0]["rank"] = 99
    report = lib.validate_ranker_response(response, merge_proposal)
    assert report["ok"] is False
    assert any("contiguous" in issue for issue in report["issues"])


def test_validate_rejects_empty_reasoning(lib, merge_proposal):
    response = _filled_response(merge_proposal)
    response["ranked_chunks"][2]["reasoning"] = "   "
    report = lib.validate_ranker_response(response, merge_proposal)
    assert report["ok"] is False
    assert any("empty reasoning" in issue for issue in report["issues"])


def test_validate_rejects_wrong_length(lib, merge_proposal):
    response = _filled_response(merge_proposal)
    response["ranked_chunks"].pop()
    report = lib.validate_ranker_response(response, merge_proposal)
    assert report["ok"] is False
    assert any("length" in issue for issue in report["issues"])


# Materialization ------------------------------------------------------------


def test_parse_ranked_chunks_sorts_by_rank(lib, merge_proposal):
    response = _filled_response(merge_proposal)
    ranked = lib.parse_ranked_chunks(response, merge_proposal)
    assert tuple(chunk.rank for chunk in ranked) == tuple(
        range(1, len(merge_proposal.all_candidates()) + 1)
    )


def test_parse_ranked_chunks_round_trips_reasoning(lib, merge_proposal):
    response = _filled_response(merge_proposal)
    ranked = lib.parse_ranked_chunks(response, merge_proposal)
    for chunk, source in zip(ranked, response["ranked_chunks"]):
        assert chunk.reasoning == source["reasoning"].strip()


# CLI round-trip -------------------------------------------------------------


def test_cli_emits_valid_packet_from_merge_proposal_stdin(tmp_path, lib, merge_proposal):
    payload = json.dumps(merge_proposal.to_dict())
    result = subprocess.run(
        ["python3", str(PACKET_SCRIPT), "--merge-proposal", "-"],
        input=payload,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    packet = json.loads(result.stdout)
    assert packet["version"] == lib.RANKER_PACKET_VERSION
    assert packet["ranker_prompt"] == lib.RANKER_PROMPT
    assert "ranked_chunks" in packet["response_schema"]["properties"]
