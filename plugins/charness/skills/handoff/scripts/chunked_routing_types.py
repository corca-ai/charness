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
    # Staleness FACTS, never a verdict. An entry whose paths moved may still be
    # real work, so nothing downstream drops an entry on these — they exist so
    # the ranking agent sees "cites 3 paths, 1 gone; cites a closed issue" BEFORE
    # planning instead of after. Empty also means "not checked" (the path check
    # needs a repo root; the issue check needs the tracker), which is why the
    # parser payload reports what was checked separately.
    missing_paths: tuple[str, ...] = ()
    closed_issues: tuple[int, ...] = ()
    # Cited issues the tracker was ASKED about and did not answer for. Distinct
    # from an absent `closed_issues` entry, which means "open" only if the check
    # ran at all.
    unresolved_issues: tuple[int, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "HandoffEntry":
        """Rebuild an entry from pipeline JSON.

        Every downstream stage (`propose_merges`, `prepare_chunk_packet`,
        `prepare_ranker_packet`, `draft_goal_from_chunk`) used to hand-roll this
        with its own literal field list, so a new field silently vanished at four
        boundaries at once. One constructor means a field added above travels the
        whole pipeline.
        """
        return cls(
            index=int(payload["index"]),
            title=payload["title"],
            body=payload["body"],
            referenced_paths=tuple(payload.get("referenced_paths", [])),
            referenced_issues=tuple(payload.get("referenced_issues", [])),
            referenced_skills=tuple(payload.get("referenced_skills", [])),
            boundary_tokens=tuple(payload.get("boundary_tokens", [])),
            missing_paths=tuple(payload.get("missing_paths", [])),
            closed_issues=tuple(int(number) for number in payload.get("closed_issues", [])),
            unresolved_issues=tuple(int(number) for number in payload.get("unresolved_issues", [])),
        )


def entries_from_payload(payload: Any) -> list[HandoffEntry]:
    """Rebuild the entry list from a parser payload OR a bare entries array.

    Every pipeline stage accepts both shapes, and each used to re-derive the
    accept-either rule beside its own reconstruction — the same accretion that
    let a new entry field vanish at four boundaries. This owns the shape; the
    stages own what they do with it.
    """
    if isinstance(payload, dict) and "entries" in payload:
        entry_dicts = payload["entries"]
    elif isinstance(payload, list):
        entry_dicts = payload
    else:
        raise ValueError("input JSON must be either a parser payload or an entries array")
    return [HandoffEntry.from_dict(entry) for entry in entry_dicts]


@dataclass(frozen=True)
class ChunkCandidate:
    entries: tuple[HandoffEntry, ...]
    label: str
    objective_summary: str
    judgment_summary: dict[str, str] | None = None

    def to_dict(self) -> dict[str, Any]:
        payload = {
            "entries": [entry.to_dict() for entry in self.entries],
            "label": self.label,
            "objective_summary": self.objective_summary,
        }
        if self.judgment_summary:
            payload["judgment_summary"] = dict(self.judgment_summary)
        return payload


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
