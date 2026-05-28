"""Merge proposer and ranked-chunk materializer for chunked routing.

Builds ``MergeProposal`` records from parsed ``HandoffEntry`` lists by
connecting entries that share at least one non-trivial boundary token,
and materializes ``RankedChunk`` records from a validated agent response.
"""
import importlib.util
from pathlib import Path
from typing import Any


def _load_sibling_types():
    spec = importlib.util.spec_from_file_location(
        "chunked_routing_types",
        Path(__file__).resolve().parent / "chunked_routing_types.py",
    )
    if spec is None or spec.loader is None:
        raise ImportError(
            "chunked_routing_types.py not found beside chunked_routing_merger.py"
        )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_types = _load_sibling_types()
HandoffEntry = _types.HandoffEntry
ChunkCandidate = _types.ChunkCandidate
MergeProposal = _types.MergeProposal
RankedChunk = _types.RankedChunk


def _candidate_label_from_entries(entries: tuple[HandoffEntry, ...]) -> str:
    """Stable label derived from a candidate's entries.

    Single-entry: ``chunk-<index>``. Multi-entry: ``chunk-<sorted-indices>``
    joined with ``-``. The label is the join key the agent uses in the
    ranker response, so it must be deterministic.
    """
    indices = sorted(entry.index for entry in entries)
    return "chunk-" + "-".join(str(index) for index in indices)


def _candidate_objective_from_entries(entries: tuple[HandoffEntry, ...]) -> str:
    """One-line objective summary for a candidate."""
    if len(entries) == 1:
        return entries[0].title
    titles = " + ".join(entry.title for entry in entries)
    return f"Bundle ({len(entries)}): {titles}"


def _build_standalone(entries: list[HandoffEntry]) -> tuple[ChunkCandidate, ...]:
    return tuple(
        ChunkCandidate(
            entries=(entry,),
            label=_candidate_label_from_entries((entry,)),
            objective_summary=_candidate_objective_from_entries((entry,)),
        )
        for entry in entries
    )


def _pairwise_shared_tokens(
    entries: list[HandoffEntry],
) -> dict[tuple[int, int], tuple[str, ...]]:
    """Return ``{(i, j): shared_tokens}`` for every entry pair with overlap."""
    shared: dict[tuple[int, int], tuple[str, ...]] = {}
    for i, left in enumerate(entries):
        left_tokens = set(left.boundary_tokens)
        if not left_tokens:
            continue
        for j in range(i + 1, len(entries)):
            right = entries[j]
            overlap = left_tokens & set(right.boundary_tokens)
            if overlap:
                shared[(i, j)] = tuple(sorted(overlap))
    return shared


def _connected_components(
    n: int, edges: list[tuple[int, int]]
) -> list[list[int]]:
    """Return connected components as lists of indices (sorted within)."""
    parent = list(range(n))

    def find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a: int, b: int) -> None:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb

    for a, b in edges:
        union(a, b)

    groups: dict[int, list[int]] = {}
    for i in range(n):
        root = find(i)
        groups.setdefault(root, []).append(i)
    return [sorted(group) for group in groups.values()]


def propose_merges(entries: list[HandoffEntry]) -> MergeProposal:
    """Build a MergeProposal from parsed handoff entries.

    Standalone candidates: one per entry. Merged candidates: one per
    connected component of size ≥ 2 in the boundary-token overlap graph.
    A pair shares a boundary when their ``boundary_tokens`` sets
    intersect; ``boundary_tokens`` is already pre-filtered by
    ``is_nontrivial_token`` so common-noun bare-directory overlaps
    (`scripts/`, `tests/`, ...) cannot trigger merges.
    """
    standalone = _build_standalone(entries)
    if len(entries) < 2:
        return MergeProposal(
            standalone=standalone,
            merged=(),
            shared_boundary_reason={},
        )
    pairwise = _pairwise_shared_tokens(entries)
    edges = list(pairwise.keys())
    components = _connected_components(len(entries), edges)
    merged: list[ChunkCandidate] = []
    reasons: dict[str, str] = {}
    for component in components:
        if len(component) < 2:
            continue
        member_entries = tuple(entries[i] for i in component)
        candidate = ChunkCandidate(
            entries=member_entries,
            label=_candidate_label_from_entries(member_entries),
            objective_summary=_candidate_objective_from_entries(member_entries),
        )
        merged.append(candidate)
        component_tokens: set[str] = set()
        for i in component:
            for j in component:
                if i >= j:
                    continue
                component_tokens.update(pairwise.get((i, j), ()))
        reasons[candidate.label] = (
            "shared boundary tokens: " + ", ".join(sorted(component_tokens))
        )
    return MergeProposal(
        standalone=standalone,
        merged=tuple(merged),
        shared_boundary_reason=reasons,
    )


def parse_ranked_chunks(
    response: dict[str, Any], merge_proposal: MergeProposal
) -> tuple[RankedChunk, ...]:
    """Materialize ``RankedChunk`` records from a validated response.

    Caller is responsible for running ``validate_ranker_response`` first;
    this function trusts the shape but skips any chunk whose label is
    unknown so a partial fail does not throw.
    """
    by_label = {
        candidate.label: candidate for candidate in merge_proposal.all_candidates()
    }
    ranked: list[RankedChunk] = []
    for entry in response.get("ranked_chunks", []):
        label = entry.get("candidate_label")
        candidate = by_label.get(label)
        if candidate is None:
            continue
        ranked.append(
            RankedChunk(
                candidate=candidate,
                rank=int(entry["rank"]),
                reasoning=str(entry["reasoning"]).strip(),
            )
        )
    ranked.sort(key=lambda chunk: chunk.rank)
    return tuple(ranked)
