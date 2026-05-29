"""Shared entrypoint for the handoff chunked-routing pipeline.

Records flow:

    parse_handoff_entries.py    -> HandoffEntry
    propose_merges.py           -> MergeProposal(standalone=[...], merged=[...])
    prepare_ranker_packet.py    -> RankerPacket (JSON for agent fill)
    draft_goal_from_chunk.py    -> consumes a selected ChunkCandidate

The records carry plain-string boundary tokens (full path strings, never
split components) so the merge proposer can compute overlap honestly. See
``docs/handoff-chunked-routing.md`` for the contract that owns this shape.

This module hosts the ranker packet builder, the ranker-response
validator, and the chunker trigger; it also re-exports the dataclasses,
parser, merger, and auto-draft helpers from sibling modules so the
``chunked_routing_lib.X`` accessor pattern keeps working for every
caller and every test.
"""
import importlib.util
import re
from pathlib import Path
from typing import Any


def _load_sibling(module_name: str):
    spec = importlib.util.spec_from_file_location(
        module_name,
        Path(__file__).resolve().parent / f"{module_name}.py",
    )
    if spec is None or spec.loader is None:
        raise ImportError(f"{module_name}.py not found beside chunked_routing_lib.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_types = _load_sibling("chunked_routing_types")
_parser = _load_sibling("chunked_routing_parser")
_merger = _load_sibling("chunked_routing_merger")
_auto_draft = _load_sibling("chunked_routing_auto_draft")

# Re-exports — types & shared utility ---------------------------------------
COMMON_NOUN_EXCLUSIONS = _types.COMMON_NOUN_EXCLUSIONS
is_nontrivial_token = _types.is_nontrivial_token
HandoffEntry = _types.HandoffEntry
ChunkCandidate = _types.ChunkCandidate
RankedChunk = _types.RankedChunk
MergeProposal = _types.MergeProposal

# Re-exports — parser -------------------------------------------------------
extract_next_session_block = _parser.extract_next_session_block
parse_handoff_entries = _parser.parse_handoff_entries
_build_boundary_tokens = _parser._build_boundary_tokens

# Re-exports — merger -------------------------------------------------------
propose_merges = _merger.propose_merges
parse_ranked_chunks = _merger.parse_ranked_chunks

# Re-exports — auto-draft ---------------------------------------------------
USER_ACCEPTANCE_PLACEHOLDER = _auto_draft.USER_ACCEPTANCE_PLACEHOLDER
AGENT_VERIFICATION_PLACEHOLDER = _auto_draft.AGENT_VERIFICATION_PLACEHOLDER
INTERVIEW_DECISIONS_PLACEHOLDER = _auto_draft.INTERVIEW_DECISIONS_PLACEHOLDER
PLAN_CRITIQUE_PLACEHOLDER = _auto_draft.PLAN_CRITIQUE_PLACEHOLDER
auto_draft_slug = _auto_draft.auto_draft_slug
render_auto_draft_artifact = _auto_draft.render_auto_draft_artifact


# Ranker packet -------------------------------------------------------------

RANKER_PACKET_VERSION = 1

# Canonical generative-sequence prompt. Mirrors the Christopher Alexander
# idiom used in skills/public/issue/SKILL.md step 5 ("the move that reduces
# uncertainty or unlocks the next issue comes first"). Pinned here so a
# prompt change forces a fixture update; the round-trip test is the gate.
RANKER_PROMPT = (
    "Rank the chunk candidates as a Christopher Alexander generative "
    "sequence: the chunk that reduces the most uncertainty for, or "
    "unlocks the most of, the remaining chunks comes first. Prefer moves "
    "that lower risk for later chunks; do not optimize for cheapest-first "
    "or for personal momentum. Do not rank by input order, alphabetical "
    "order, or any other ordering that ignores the unlock relation between "
    "chunks.\n\n"
    "For each candidate (standalone or merged), assign:\n"
    "- candidate_label: the candidate's `label` field verbatim\n"
    "- rank: integer starting at 1; ranks must be a contiguous 1..N\n"
    "  permutation of all candidates with no gaps or duplicates\n"
    "- reasoning: 2-3 sentences naming what this chunk unlocks for the\n"
    "  next chunk, what uncertainty it removes, or which downstream\n"
    "  decision becomes cheaper. Do not restate the chunk's objective\n"
    "  summary — the reasoning explains why this position in the\n"
    "  sequence is right.\n\n"
    "Reasoning must be non-empty for every candidate so a later "
    '"why not chunk X?" follow-up can be answered from this rendered '
    "output without re-running the ranker."
)


_RESPONSE_SCHEMA = {
    "type": "object",
    "required": ["ranked_chunks"],
    "properties": {
        "ranked_chunks": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["candidate_label", "rank", "reasoning"],
                "properties": {
                    "candidate_label": {"type": "string", "minLength": 1},
                    "rank": {"type": "integer", "minimum": 1},
                    "reasoning": {"type": "string", "minLength": 1},
                },
            },
        }
    },
}


def build_ranker_packet(merge_proposal: MergeProposal) -> dict[str, Any]:
    """Return the JSON-serializable packet handed to the agent ranker.

    The packet is self-contained: the agent fills the response shape
    declared in ``response_schema`` and the parent calls
    ``validate_ranker_response`` on the filled payload. No follow-up
    fetch is needed.
    """
    return {
        "version": RANKER_PACKET_VERSION,
        "merge_proposal": merge_proposal.to_dict(),
        "ranker_prompt": RANKER_PROMPT,
        "response_schema": _RESPONSE_SCHEMA,
    }


def _expected_labels(merge_proposal: MergeProposal) -> list[str]:
    return [candidate.label for candidate in merge_proposal.all_candidates()]


def validate_ranker_response(
    response: dict[str, Any], merge_proposal: MergeProposal
) -> dict[str, Any]:
    """Validate an agent-filled ranker response.

    Returns ``{"ok": bool, "issues": [...]}``. Issues to report:

    - missing ``ranked_chunks`` key or non-list shape
    - wrong length (must equal total candidate count)
    - duplicate or unknown ``candidate_label`` values
    - ranks are not a contiguous 1..N permutation
    - any chunk has empty ``reasoning``
    """
    issues: list[str] = []
    expected = _expected_labels(merge_proposal)
    expected_set = set(expected)

    ranked = response.get("ranked_chunks")
    if not isinstance(ranked, list):
        return {"ok": False, "issues": ["missing or non-list `ranked_chunks`"]}

    if len(ranked) != len(expected):
        issues.append(
            f"ranked_chunks length {len(ranked)} != candidate count {len(expected)}"
        )

    seen_labels: set[str] = set()
    seen_ranks: list[int] = []
    for entry in ranked:
        if not isinstance(entry, dict):
            issues.append(f"non-dict entry: {entry!r}")
            continue
        label = entry.get("candidate_label")
        rank = entry.get("rank")
        reasoning = entry.get("reasoning")
        if not isinstance(label, str) or not label:
            issues.append(f"missing/empty candidate_label in {entry!r}")
            continue
        if label not in expected_set:
            issues.append(f"unknown candidate_label {label!r}")
        if label in seen_labels:
            issues.append(f"duplicate candidate_label {label!r}")
        seen_labels.add(label)
        if not isinstance(rank, int) or rank < 1:
            issues.append(f"invalid rank {rank!r} for {label!r}")
        else:
            seen_ranks.append(rank)
        if not isinstance(reasoning, str) or not reasoning.strip():
            issues.append(f"empty reasoning for {label!r}")

    if seen_ranks:
        expected_ranks = list(range(1, len(expected) + 1))
        if sorted(seen_ranks) != expected_ranks:
            issues.append(
                f"ranks {sorted(seen_ranks)} != contiguous 1..{len(expected)}"
            )

    return {"ok": not issues, "issues": issues}


# Trigger detection --------------------------------------------------------

# The chunker fires iff a user invocation references the handoff surface
# *and* contains no explicit task directive. The rule is deterministic so
# slice 6 SKILL.md prose, slice 7 verification, and the spec fixture all
# consult the same source.

_HANDOFF_MENTION_PATTERNS = (
    r"\bdocs/handoff\.md\b",
    r"\bhandoff\.md\b",
    r"/handoff\b",
    r"\bhandoff[ -]skill\b",
    r"\bcharness:handoff\b",
    r"\bhandoff[ ]?스킬\b",
    r"\b(?:read|check|see)\s+(?:the\s+)?handoff\b",
    r"\bwhat'?s\s+(?:in|next)\s+(?:in\s+)?(?:the\s+)?handoff\b",
    r"\bnext\s+from\s+handoff\b",
    r"\bpick\s+up\s+from\s+handoff\b",
    r"\b핸드오프\b",
)

_TASK_DIRECTIVE_PATTERNS = (
    # Imperative verb + non-handoff noun. Pattern matches a verb followed
    # by at least one word that is not 'handoff' / 'the handoff'.
    (
        r"\b(?:do|fix|implement|close|push|run|start|work\s+on|resolve|"
        r"merge|release|revert)\s+"
        r"(?!the\s+handoff\b|handoff\b)\S+"
    ),
    # Explicit issue id.
    r"#\d+",
    # File path other than the handoff itself (anything matching path/file.ext
    # where the path is NOT docs/handoff.md or handoff.md).
    (
        r"(?<![A-Za-z0-9_])(?!docs/handoff\.md\b|handoff\.md\b)"
        r"(?:[A-Za-z0-9_.-]+/)+[A-Za-z0-9_.-]+\.[A-Za-z]{1,8}\b"
    ),
    # Slash command other than /handoff.
    r"/(?!handoff\b)[A-Za-z][A-Za-z0-9_-]*",
    # CLI flag.
    r"\s--[A-Za-z][A-Za-z0-9-]*\b",
)


def _matches_any(patterns: tuple[str, ...], text: str) -> bool:
    return any(re.search(pattern, text, re.IGNORECASE) for pattern in patterns)


def should_fire_chunker(user_message: str, *, invoked_directly: bool = False) -> bool:
    """Return True iff the chunker should fire for ``user_message``.

    The rule is deterministic. The chunker fires iff there is no explicit task
    directive AND one of:
    (a) the message references the handoff surface — file, ``/handoff``, skill
        id, or a canonical pickup phrase (including Korean); or
    (b) ``invoked_directly`` is True — the handoff skill was launched directly
        with no task (e.g. a bare ``/handoff`` / ``charness:handoff`` call), the
        #249 trigger-widening path.

    An explicit task directive (imperative verb + non-handoff noun, issue id,
    non-handoff file path, slash command other than /handoff, or CLI flag)
    always bypasses — even on a direct invocation that carries one
    (``/handoff fix #233`` does not fire).

    See ``skills/public/handoff/references/chunked-routing.md`` for the
    operator-facing rule and the trigger fixture in
    ``tests/test_handoff_chunker_trigger.py``.
    """
    message = user_message or ""
    if message.strip() and _matches_any(_TASK_DIRECTIVE_PATTERNS, message):
        return False
    if invoked_directly:
        return True
    if not message.strip():
        return False
    if not _matches_any(_HANDOFF_MENTION_PATTERNS, message):
        return False
    return True
