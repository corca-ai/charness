"""Shared dataclasses and the boundary-token utility for chunked routing.

Records flow:

    parse_handoff_entries.py    -> HandoffEntry
    propose_merges.py           -> deterministic MergeProposal hints
    prepare_chunk_packet.py     -> agentic work-package proposal packet
    prepare_ranker_packet.py    -> RankerPacket (JSON for agent fill)
    draft_goal_from_chunk.py    -> consumes a selected ChunkCandidate

The records carry plain-string boundary tokens (full path strings, never
split components) so the merge proposer can compute overlap honestly. See
``references/chunked-routing.md`` for the contract (in the charness source
repo the full implementation contract is ``docs/handoff-chunked-routing.md``,
which is not vendored with the skill).
"""
from dataclasses import asdict, dataclass
from typing import Any

COMMON_NOUN_EXCLUSIONS = frozenset(
    {"docs", "skills", "scripts", "tests", ".githooks", "plugins", "integrations"}
)


def is_nontrivial_token(token: str) -> bool:
    """A boundary token is non-trivial when it survives merge tokenization.

    Per the spec: a non-trivial token contains at least one path separator
    AND is not in the common-noun exclusion set. Bare directory roots like
    ``scripts/`` do not count; two entries must share a deeper sub-path
    like ``skills/public/handoff/`` to merge.
    """
    if not token:
        return False
    stripped = token.rstrip("/")
    if stripped in COMMON_NOUN_EXCLUSIONS:
        return False
    return "/" in stripped


@dataclass(frozen=True)
class HandoffEntry:
    index: int
    title: str
    body: str
    referenced_paths: tuple[str, ...] = ()
    referenced_issues: tuple[int, ...] = ()
    referenced_skills: tuple[str, ...] = ()
    boundary_tokens: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ChunkCandidate:
    entries: tuple[HandoffEntry, ...]
    label: str
    objective_summary: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "entries": [entry.to_dict() for entry in self.entries],
            "label": self.label,
            "objective_summary": self.objective_summary,
        }


@dataclass(frozen=True)
class RankedChunk:
    candidate: ChunkCandidate
    rank: int
    reasoning: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "candidate": self.candidate.to_dict(),
            "rank": self.rank,
            "reasoning": self.reasoning,
        }


@dataclass(frozen=True)
class MergeProposal:
    standalone: tuple[ChunkCandidate, ...]
    merged: tuple[ChunkCandidate, ...]
    shared_boundary_reason: dict[str, str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "standalone": [candidate.to_dict() for candidate in self.standalone],
            "merged": [candidate.to_dict() for candidate in self.merged],
            "shared_boundary_reason": dict(self.shared_boundary_reason),
        }

    def all_candidates(self) -> tuple[ChunkCandidate, ...]:
        return tuple(self.standalone) + tuple(self.merged)
