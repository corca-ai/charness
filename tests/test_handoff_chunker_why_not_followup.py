"""Slice 3 why-not follow-up contract.

The goal artifact's User Acceptance criterion: when the user asks
"why not chunk X?" in the same conversational turn, the agent must
answer using the already-computed reasoning from the rendered ranker
output rather than re-invoking the ranker.

The test target is the contract: every RankedChunk that comes out of
the validator + materializer must carry a non-empty ``reasoning``
field, so a follow-up answer can be sourced from the rendered output
without re-running the agent.
"""
from __future__ import annotations

import importlib.util
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
    text = FIXTURE_PATH.read_text(encoding="utf-8")
    entries = lib.parse_handoff_entries(text)
    standalone = tuple(
        lib.ChunkCandidate(
            entries=(entry,),
            label=f"chunk-{entry.index}",
            objective_summary=entry.title,
        )
        for entry in entries
    )
    return lib.MergeProposal(
        standalone=standalone,
        merged=(),
        shared_boundary_reason={},
    )


def _filled_response(merge_proposal) -> dict:
    """Filled response with reasoning text that follows the prompt's rule.

    Each chunk names what it *unlocks* for the next ranked chunk rather
    than restating its own objective_summary, so the fixture does not
    teach the anti-pattern the prompt explicitly forbids.
    """
    candidates = merge_proposal.all_candidates()
    labels = [candidate.label for candidate in candidates]
    return {
        "ranked_chunks": [
            {
                "candidate_label": candidate.label,
                "rank": index + 1,
                "reasoning": (
                    f"Comes at position {index + 1} because resolving it "
                    f"removes the uncertainty that chunk "
                    f"`{labels[index + 1]}` would otherwise hit."
                )
                if index < len(labels) - 1
                else (
                    "Comes last; every dependency has been removed by "
                    "the earlier ranks, so this chunk no longer blocks."
                ),
            }
            for index, candidate in enumerate(candidates)
        ]
    }


def test_every_ranked_chunk_carries_nonempty_reasoning_for_followup(
    lib, merge_proposal
):
    """A 'why not chunk N?' follow-up must be answerable from the
    rendered ranker output without re-running the ranker.

    The validator's contract is that every chunk has non-empty reasoning;
    this test pins the User Acceptance criterion explicitly so a future
    schema change that allowed empty reasoning would fail this test
    before it could regress the follow-up flow.
    """
    response = _filled_response(merge_proposal)
    validation = lib.validate_ranker_response(response, merge_proposal)
    assert validation["ok"] is True, validation["issues"]
    ranked = lib.parse_ranked_chunks(response, merge_proposal)
    assert len(ranked) == len(merge_proposal.all_candidates())
    for chunk in ranked:
        assert chunk.reasoning, (
            f"chunk {chunk.candidate.label} has empty reasoning; the "
            "why-not follow-up cannot answer from already-computed reasoning"
        )


def test_followup_simulation_uses_precomputed_reasoning(lib, merge_proposal):
    """Simulate the conversational follow-up: user asks 'why not chunk N?'.

    The agent must answer from the rendered RankedChunk.reasoning, not
    by re-invoking the ranker. The simulation here returns the exact
    pre-computed string keyed by candidate label, asserting the data
    needed for the follow-up is fully present.
    """
    response = _filled_response(merge_proposal)
    ranked = lib.parse_ranked_chunks(response, merge_proposal)
    by_label = {chunk.candidate.label: chunk for chunk in ranked}

    def answer_followup(question_label: str) -> str:
        # The agent at conversation time looks up reasoning by label;
        # no new tool call, no re-rank.
        return by_label[question_label].reasoning

    for candidate in merge_proposal.all_candidates():
        answer = answer_followup(candidate.label)
        assert answer
        assert isinstance(answer, str)
