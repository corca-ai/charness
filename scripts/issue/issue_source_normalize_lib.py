"""Deterministic normalization of captured issue source into a clause inventory.

The acceptance matrix has to point at *something stable* inside an issue. Pointing
at "the third bullet of #518" is not stable: editing a comment, or GitHub returning
comments in a different order, silently re-aims every such pointer at different
text while every id still resolves. This module makes that impossible by deriving
each clause id from frozen components — the snapshot digest, an immutable source
unit id, the clause's ordinal within that unit, and the digest of the clause text
itself. Reordering changes the unit/ordinal; editing changes the clause digest;
recapturing changed source changes the snapshot digest. Any of the three
invalidates the id, so a stale pointer fails loudly instead of aiming somewhere new.

The normalization policy is versioned (`github-issue-v1`) and recorded in the
receipt, because "what counts as one clause" is exactly the kind of decision that
drifts silently and takes every derived id with it.
"""

from __future__ import annotations

import hashlib
import json
import re
from typing import Any

NORMALIZATION_POLICY = "github-issue-v1"

# A fence may be blockquoted (issue bodies routinely quote a prior comment wholesale)
# and may sit at any indent inside a list item. The old `^\s{0,3}` form missed both, so
# quoted evidence was parsed as ordinary markdown and its `- ` lines became criteria.
_FENCE_RE = re.compile(r"^[\s>]*(`{3,}|~{3,})(?P<info>.*)$")
# No indent ceiling: a bullet nested four levels deep is still a bullet, and the old
# 7-space limit silently folded it into its parent so it could never carry its own
# disposition under the crosswalk's per-clause floor.
#
# There is deliberately NO indented-code rule here, and that is a considered trade
# rather than an omission. A four-space-indented block is markdown's other code form,
# so treating it as code would stop pasted evidence minting bullet-shaped clauses — but
# a nested list item is ALSO indented four-plus spaces, and inside a list markdown reads
# it as a bullet, not code. Distinguishing them needs real CommonMark list-context
# tracking. An earlier revision added the code rule without that context and it ate
# every deeply-nested bullet, reintroducing the exact under-splitting it was added
# alongside a fix for.
#
# Given the ambiguity, over-splitting is the safe direction: a spurious clause still
# receives an explicit disposition in the crosswalk (`non-goal` / `evidence-only` with a
# reason and owner), so it costs a reviewer one line. An under-split clause is a real
# acceptance criterion that can never carry a disposition and never fails anything.
_LIST_ITEM_RE = re.compile(r"^\s*(?:[-*+]\s+|\d{1,3}[.)]\s+)")
_HEADING_RE = re.compile(r"^[\s>]*#{1,6}\s+")
_TABLE_ROW_RE = re.compile(r"^\s{0,3}\|")
_WHITESPACE_RE = re.compile(r"\s+")

DIGEST_WIDTH = 16


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def canonical_json(payload: Any) -> str:
    """One canonical serialization for everything that gets digested.

    Every digest in this lane must be reproducible from the payload alone, by any
    reader, in any order the fields happen to be built. `sort_keys` plus fixed
    separators is what makes recomputing a digest a real check rather than a
    re-serialization coincidence.
    """
    return json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_payload(payload: Any) -> str:
    return sha256_text(canonical_json(payload))


def _normalize_text(raw: str) -> str:
    text = raw.replace("\r\n", "\n").replace("\r", "\n").replace(" ", " ")
    return "\n".join(line.rstrip() for line in text.split("\n"))


def _clause_key(text: str) -> str:
    """Whitespace-insensitive form used for the clause digest.

    Line wrapping inside one bullet is a rendering detail, not a semantic change, so
    the digest ignores it. BUT DO NOT READ THAT AS REWRAP TOLERANCE FOR CLAUSE IDS: the
    id folds in `source_snapshot_sha256`, a digest over the WHOLE document, so any edit
    anywhere — including a rewrap, and including a new comment on a different issue in
    the same snapshot — changes every clause id in the snapshot. That whole-snapshot
    anchoring is the goal's explicit contract (source changes must invalidate the old
    inventory), and its cost is that re-freezing is a routine act rather than a rare
    one. What this normalization actually buys is a stable `clause_digest` for
    diagnostics and diffing across freezes; it does not make ids survive a rewrap, and
    an earlier version of this docstring claimed it did.
    """
    return _WHITESPACE_RE.sub(" ", text).strip()


def _opens_a_fence(match: "re.Match[str]") -> bool:
    """CommonMark: a BACKTICK fence's info string may not contain a backtick.

    Without this, a line-initial inline-code span like ```` ```make test``` fails ````
    reads as a fence opener and swallows the entire rest of the unit — collapsing every
    following bullet into one clause. GitHub renders that line as inline code, so the
    bullets after it really are criteria, and treating them as fenced evidence would hide
    them. Tilde fences have no such restriction.
    """
    if not match.group(1).startswith("`"):
        return True
    return "`" not in match.group("info")


def split_clauses(raw: str) -> list[str]:
    """Split one issue body/comment into normalized clauses.

    Fenced blocks are emitted whole and verbatim-ish (normalized line endings only):
    a fence is pasted evidence — a log, a diff, a command transcript — and splitting
    it on its bullet-looking lines would mint criterion-shaped clauses out of quoted
    output. Outside fences, a heading, list item, or table row begins a new clause
    and its continuation lines fold into it, so a wrapped bullet stays one clause.

    An UNTERMINATED fence runs to the end of the unit and yields one clause. That looks
    alarming — a stray ``` collapsing every following bullet into one blob — and it is
    nonetheless correct, because it is exactly what GitHub renders: those bullets ARE
    inside a code block for every human reading the issue. An earlier revision raised on
    this instead. That was wrong twice over: it made a common typo in someone else's
    issue body a hard failure of this repo's capture, and it would have split text into
    "criteria" that no reader of the issue can see as criteria. Matching the source of
    truth beats second-guessing it.
    """
    text = _normalize_text(raw)
    clauses: list[str] = []
    current: list[str] = []
    fence: str | None = None

    def flush() -> None:
        if current:
            joined = "\n".join(current).strip()
            if joined:
                clauses.append(joined)
            current.clear()

    for line in text.split("\n"):
        if fence is not None:
            current.append(line)
            if line.strip().lstrip("> ").startswith(fence):
                flush()
                fence = None
            continue
        fence_match = _FENCE_RE.match(line)
        if fence_match and _opens_a_fence(fence_match):
            flush()
            fence = fence_match.group(1)
            current.append(line)
            continue
        if not line.strip():
            flush()
            continue
        if _HEADING_RE.match(line) or _LIST_ITEM_RE.match(line) or _TABLE_ROW_RE.match(line):
            flush()
        current.append(line)
    flush()
    return clauses


def body_source_unit_id(number: int) -> str:
    return f"{number}:body"


def comment_source_unit_id(number: int, node_id: str) -> str:
    return f"{number}:comment:{node_id}"


def build_source_document(repo: str, issues: list[dict[str, Any]]) -> dict[str, Any]:
    """The canonical source payload whose digest anchors every derived id.

    Deliberately narrow: number, title, body, state, and the full comment node set
    with ids. Volatile fields (`updatedAt`, reaction counts, viewer permissions)
    are excluded because they change without the source changing, and folding them
    in would invalidate the whole inventory on a no-op recapture — which trains the
    operator to re-freeze reflexively and defeats the staleness check entirely.
    """
    return {
        "repository": repo,
        "normalization_policy": NORMALIZATION_POLICY,
        "issues": [
            {
                "number": issue["number"],
                "title": issue.get("title") or "",
                "state": issue.get("state") or "",
                "body": _normalize_text(issue.get("body") or ""),
                "comment_total_count": issue["comment_total_count"],
                "comments": [
                    {
                        "id": comment["id"],
                        "author": comment.get("author") or "",
                        "created_at": comment.get("created_at") or "",
                        "body": _normalize_text(comment.get("body") or ""),
                    }
                    for comment in issue["comments"]
                ],
            }
            for issue in sorted(issues, key=lambda item: item["number"])
        ],
    }


def _unit_records(issue: dict[str, Any]) -> list[tuple[str, str, str]]:
    number = issue["number"]
    units = [(body_source_unit_id(number), "body", issue["body"])]
    units.extend(
        (comment_source_unit_id(number, comment["id"]), "comment", comment["body"])
        for comment in issue["comments"]
    )
    return units


def build_clause_inventory(document: dict[str, Any]) -> dict[str, Any]:
    """Clause inventory + the snapshot digest every clause id is bound to.

    The digest is taken over `document` BEFORE any id is assigned, so there is no
    circularity: ids are a function of the frozen source, never of the file that
    stores them.
    """
    snapshot_sha256 = sha256_payload(document)
    issues: list[dict[str, Any]] = []
    for issue in document["issues"]:
        units: list[dict[str, Any]] = []
        for unit_id, kind, text in _unit_records(issue):
            clauses = split_clauses(text)
            units.append(
                {
                    "source_unit_id": unit_id,
                    "kind": kind,
                    "empty": not clauses,
                    "clause_count": len(clauses),
                    "clauses": [
                        _clause_record(snapshot_sha256, unit_id, ordinal, clause)
                        for ordinal, clause in enumerate(clauses)
                    ],
                }
            )
        issues.append(
            {
                "number": issue["number"],
                "source_units": units,
                "clause_count": sum(unit["clause_count"] for unit in units),
            }
        )
    return {
        "normalization_policy": NORMALIZATION_POLICY,
        "source_snapshot_sha256": snapshot_sha256,
        "issues": issues,
    }


def _clause_record(snapshot_sha256: str, unit_id: str, ordinal: int, clause: str) -> dict[str, Any]:
    clause_key = _clause_key(clause)
    clause_digest = sha256_text(clause_key)[:DIGEST_WIDTH]
    identity = f"{snapshot_sha256}|{unit_id}|{ordinal}|{clause_digest}"
    return {
        "source_clause_id": sha256_text(identity)[:DIGEST_WIDTH],
        "source_unit_id": unit_id,
        "ordinal": ordinal,
        "clause_digest": clause_digest,
        "source_snapshot_sha256": snapshot_sha256,
        "excerpt": clause_key[:280],
    }


def clause_inventory_identity(inventory: dict[str, Any]) -> str:
    """Identity of the inventory itself, independent of excerpt rendering.

    Only the structural facts — which units exist, in which order, with which
    clause ids — participate. An excerpt-width or rendering change must not read as
    a source change, and a real source change cannot hide behind an unchanged
    excerpt because the clause ids already encode the digests.
    """
    skeleton = [
        {
            "number": issue["number"],
            "units": [
                {
                    "source_unit_id": unit["source_unit_id"],
                    "clause_ids": [clause["source_clause_id"] for clause in unit["clauses"]],
                }
                for unit in issue["source_units"]
            ],
        }
        for issue in inventory["issues"]
    ]
    return sha256_payload(
        {
            "normalization_policy": inventory["normalization_policy"],
            "source_snapshot_sha256": inventory["source_snapshot_sha256"],
            "issues": skeleton,
        }
    )
