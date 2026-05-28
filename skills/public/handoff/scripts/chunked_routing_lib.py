"""Shared dataclasses and helpers for the handoff chunked-routing pipeline.

Records flow:

    parse_handoff_entries.py    -> HandoffEntry
    propose_merges.py           -> MergeProposal(standalone=[...], merged=[...])
    prepare_ranker_packet.py    -> RankerPacket (JSON for agent fill)
    draft_goal_from_chunk.py    -> consumes a selected ChunkCandidate

The records carry plain-string boundary tokens (full path strings, never
split components) so the merge proposer can compute overlap honestly. See
``docs/handoff-chunked-routing.md`` for the contract that owns this shape.
"""
import re
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


# Parsing -------------------------------------------------------------------

_H2 = re.compile(r"^## (.+?)\s*$", re.MULTILINE)
_NEXT_SESSION_HEADER = "Next Session"
_NUMBERED_BULLET = re.compile(r"^(\d+)\.\s+(.*)$")
_BOLD_TITLE = re.compile(r"^\*\*(.+?)\*\*", re.DOTALL)
_MARKDOWN_LINK = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
_ISSUE_REF = re.compile(r"#(\d+)\b")
_SKILL_PATH = re.compile(r"skills/(?:public|support|profile)/([a-z0-9-]+)")
_BARE_PATH = re.compile(
    r"(?<![\w/])("
    # file with extension: at least one path segment then file.ext
    r"(?:[a-z0-9_.-]+/)+[a-z0-9_.-]+\.[a-z]{1,6}"
    r"|"
    # multi-segment directory token: ≥2 segments ending in /
    r"(?:[a-z0-9_.-]+/){2,}"
    r")"
)
_WHITESPACE = re.compile(r"\s+")


def extract_next_session_block(text: str) -> str:
    """Return the body of ``## Next Session`` from the handoff markdown.

    Returns an empty string if the section is absent.
    """
    headings = list(_H2.finditer(text))
    for index, match in enumerate(headings):
        if match.group(1).strip() != _NEXT_SESSION_HEADER:
            continue
        body_start = text.find("\n", match.start())
        body_start = body_start + 1 if body_start != -1 else match.end()
        body_end = headings[index + 1].start() if index + 1 < len(headings) else len(text)
        return text[body_start:body_end]
    return ""


def _split_numbered_items(block: str) -> list[tuple[int, str]]:
    """Split a numbered-list block into ``(index, raw_text)`` tuples."""
    items: list[tuple[int, str]] = []
    current_lines: list[str] = []
    current_index: int | None = None
    for line in block.splitlines():
        match = _NUMBERED_BULLET.match(line)
        if match:
            if current_index is not None:
                items.append((current_index, "\n".join(current_lines).rstrip()))
            current_index = int(match.group(1))
            current_lines = [match.group(2)]
        else:
            if current_index is not None:
                current_lines.append(line)
    if current_index is not None:
        items.append((current_index, "\n".join(current_lines).rstrip()))
    return items


def _extract_title(raw_text: str) -> tuple[str, str]:
    """Split a numbered-bullet body into ``(title, remaining_body)``.

    The title is the leading ``**Bold Title.**`` phrase, with internal
    whitespace collapsed (so a soft-wrapped bold title returns as one
    line). When there is no bold-leading marker, the first sentence
    (up to the first period) is the title and the full text is preserved
    as body.
    """
    stripped = raw_text.strip()
    bold_match = _BOLD_TITLE.match(stripped)
    if bold_match:
        raw_title = bold_match.group(1).rstrip(".").strip()
        title = _WHITESPACE.sub(" ", raw_title)
        remainder = stripped[bold_match.end():].lstrip()
        return title, remainder
    period = stripped.find(".")
    if period == -1:
        return stripped, stripped
    return _WHITESPACE.sub(" ", stripped[:period].strip()), stripped


def _collect_paths(text: str) -> tuple[tuple[str, ...], tuple[str, ...]]:
    """Return ``(markdown_link_targets, bare_path_tokens)`` from ``text``.

    Markdown link targets are deduped in first-seen order. Bare path tokens
    are extension-bearing or trailing-slash directory tokens; URLs (anything
    with a scheme) are excluded.
    """
    link_targets: list[str] = []
    seen_links: set[str] = set()
    for target in _MARKDOWN_LINK.findall(text):
        cleaned = target.split("#", 1)[0].split(" ", 1)[0]
        if cleaned.startswith(("http://", "https://", "mailto:")):
            continue
        if cleaned not in seen_links:
            seen_links.add(cleaned)
            link_targets.append(cleaned)
    bare: list[str] = []
    seen_bare: set[str] = set()
    for match in _BARE_PATH.finditer(text):
        token = match.group(1)
        if token in seen_bare:
            continue
        seen_bare.add(token)
        bare.append(token)
    return tuple(link_targets), tuple(bare)


def _normalize_path(token: str) -> str:
    """Strip ``../`` and ``./`` prefixes so two link forms canonicalize."""
    stripped = token.strip()
    while stripped.startswith(("./", "../")):
        if stripped.startswith("./"):
            stripped = stripped[2:]
        else:
            stripped = stripped[3:]
    return stripped


def _collect_issues(text: str) -> tuple[int, ...]:
    seen: list[int] = []
    seen_set: set[int] = set()
    for match in _ISSUE_REF.finditer(text):
        number = int(match.group(1))
        if number not in seen_set:
            seen_set.add(number)
            seen.append(number)
    return tuple(seen)


def _collect_skills(paths: tuple[str, ...]) -> tuple[str, ...]:
    """Return canonical ``skills/public/<id>/`` tokens from referenced paths."""
    seen: list[str] = []
    seen_set: set[str] = set()
    for path in paths:
        normalized = _normalize_path(path)
        match = _SKILL_PATH.search(normalized)
        if not match:
            continue
        skill_id = match.group(1)
        canonical = f"skills/public/{skill_id}/"
        if canonical not in seen_set:
            seen_set.add(canonical)
            seen.append(canonical)
    return tuple(seen)


def _build_boundary_tokens(
    referenced_paths: tuple[str, ...], referenced_skills: tuple[str, ...]
) -> tuple[str, ...]:
    """Return the deduped non-trivial token set used for merge proposals."""
    seen: list[str] = []
    seen_set: set[str] = set()
    candidates = list(referenced_paths) + list(referenced_skills)
    for raw in candidates:
        token = _normalize_path(raw)
        if not is_nontrivial_token(token):
            continue
        if token in seen_set:
            continue
        seen_set.add(token)
        seen.append(token)
    return tuple(seen)


def parse_handoff_entries(text: str) -> list[HandoffEntry]:
    """Parse the ``## Next Session`` block of a handoff markdown body."""
    block = extract_next_session_block(text)
    if not block.strip():
        return []
    entries: list[HandoffEntry] = []
    for index, raw_text in _split_numbered_items(block):
        title, body = _extract_title(raw_text)
        link_paths, bare_paths = _collect_paths(raw_text)
        # Dedup after normalization so `../foo.md` and `foo.md` count once.
        normalized_paths: list[str] = []
        seen_normalized: set[str] = set()
        for token in list(link_paths) + list(bare_paths):
            canonical = _normalize_path(token)
            if canonical in seen_normalized:
                continue
            seen_normalized.add(canonical)
            normalized_paths.append(canonical)
        referenced_issues = _collect_issues(raw_text)
        referenced_skills = _collect_skills(tuple(normalized_paths))
        boundary_tokens = _build_boundary_tokens(
            tuple(normalized_paths), referenced_skills
        )
        entries.append(
            HandoffEntry(
                index=index,
                title=title,
                body=body,
                referenced_paths=tuple(normalized_paths),
                referenced_issues=referenced_issues,
                referenced_skills=referenced_skills,
                boundary_tokens=boundary_tokens,
            )
        )
    return entries
