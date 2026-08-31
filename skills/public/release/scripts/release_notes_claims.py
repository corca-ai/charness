#!/usr/bin/env python3

"""Render, read, and judge the derived claim block inside a release note.

Two surfaces live in one note and they are held differently.

The DERIVED BLOCK is generated wholesale from `release_claim_surfaces` and
compared back per surface chunk at publish, whitespace-normalized (the
generated notice above the first surface mark is not compared). Nothing in a
chunk is authored, so a difference there is either a hand-edit or a tree that
moved after generation — the
recorded failure mode, where notes correct on the day they were written were
contradicted by the tree at publish time.

The MARKERS are the authored side: `{{claim:<surface>.<field>=<value>}}` written
inline in prose, carrying the value they assert next to the sentence that
asserts it. That placement is the whole point. The prepared `6.0.0` notes said
*"twelve public skill scripts still declare one"* over a measured zero; a
check that only compared a block at the bottom of the file would have passed
that sentence, because the sentence is prose. The marker puts the digit under
derivation at the exact place a reader believes it.

Direction is reported, not just difference. A note claiming MORE than the tree
has is the direction that actually failed and the direction a consumer acts on, so
`over-claim` is named separately from `under-claim` rather than both collapsing
into "mismatch".
"""
from __future__ import annotations

import json
import re
import runpy
from pathlib import Path
from types import SimpleNamespace


def _load_skill_runtime_bootstrap():
    bootstrap = next((ancestor / "skill_runtime_bootstrap.py" for ancestor in Path(__file__).resolve().parents if (ancestor / "skill_runtime_bootstrap.py").is_file()), None)
    if bootstrap is None:
        raise ImportError("skill_runtime_bootstrap.py not found")
    return SimpleNamespace(**runpy.run_path(str(bootstrap)))


SKILL_RUNTIME = _load_skill_runtime_bootstrap()
_surfaces = SKILL_RUNTIME.load_local_skill_module(__file__, "release_claim_surfaces")
_yaml_output = SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.yaml_output")
render_yaml = _yaml_output.render_yaml
derive_surfaces = _surfaces.derive_surfaces
surface_field = _surfaces.surface_field
RENDERABLE_FIELDS = _surfaces.RENDERABLE_FIELDS

BLOCK_BEGIN = "<!-- charness:derived-claims:begin -->"
BLOCK_END = "<!-- charness:derived-claims:end -->"
_SURFACE_MARK = "<!-- claim-surface: {surface_id} -->"
_SURFACE_MARK_RE = re.compile(r"^<!-- claim-surface: ([a-z0-9][a-z0-9-]*) -->$")

_GENERATED_NOTICE = (
    "<!-- Generated from the shipped tree. Hand-edits are refused at publish: "
    "the gate re-derives this block and compares. -->"
)

#: `{{claim:<surface>.<field>=<value>}}`. The value runs to the closing braces,
#: so it may contain spaces and commas — an `items` claim is a comma-joined list
#: and splitting on the first comma would truncate it into a false mismatch.
CLAIM_MARKER_RE = re.compile(r"\{\{claim:([a-z0-9][a-z0-9-]*)\.([a-z_]+)=([^}]*)\}\}")


def render_surface_chunk(derived: dict[str, object]) -> str:
    """One surface, as its comment mark plus a fenced YAML body.

    Fenced because a release note is git-tracked markdown that this repo lints:
    an unfenced `unscanned:` list of sentences trips list and line-length rules,
    and an author's remedy for that is to reflow the block — i.e. to hand-edit
    the one region that must not be hand-edited.
    """
    body = render_yaml(
        {
            "id": derived["id"],
            "question": derived["question"],
            "count": derived["count"],
            "items": derived["items"],
            "scanned": derived["scanned"],
            "unscanned": derived["unscanned"],
        }
    ).rstrip("\n")
    mark = _SURFACE_MARK.format(surface_id=derived["id"])
    return f"{mark}\n\n```yaml\n{body}\n```"


def render_derived_block(derived_surfaces: list[dict[str, object]]) -> str:
    chunks = "\n\n".join(render_surface_chunk(derived) for derived in derived_surfaces)
    return f"{BLOCK_BEGIN}\n{_GENERATED_NOTICE}\n\n{chunks}\n\n{BLOCK_END}"


def _normalized(text: str) -> str:
    return "\n".join(line.rstrip() for line in text.strip().splitlines())


def extract_block_body(text: str) -> tuple[str | None, list[dict[str, object]]]:
    """The text between the block markers, plus any structural finding.

    An unterminated block returns `None` with a finding rather than reading to
    end-of-file. Reading to EOF would swallow every later section into the
    "derived" region and then report the whole tail as a mismatch, which names
    the wrong problem to the operator holding a missing `-->`.
    """
    begins = text.count(BLOCK_BEGIN)
    ends = text.count(BLOCK_END)
    if begins == 0:
        return None, [
            {
                "kind": "missing-derived-block",
                "direction": "unresolvable",
                "surface": None,
                "detail": (
                    f"the notes carry no `{BLOCK_BEGIN}` block, so no claim surface in them is "
                    "derived from the tree. Regenerate with generate_release_notes.py."
                ),
            }
        ]
    if begins > 1 or ends != 1:
        return None, [
            {
                "kind": "malformed-derived-block",
                "direction": "unresolvable",
                "surface": None,
                "detail": (
                    f"expected exactly one `{BLOCK_BEGIN}` ... `{BLOCK_END}` pair, found "
                    f"{begins} begin and {ends} end marker(s)."
                ),
            }
        ]
    start = text.index(BLOCK_BEGIN) + len(BLOCK_BEGIN)
    end = text.index(BLOCK_END)
    if end < start:
        return None, [
            {
                "kind": "malformed-derived-block",
                "direction": "unresolvable",
                "surface": None,
                "detail": f"`{BLOCK_END}` appears before `{BLOCK_BEGIN}`.",
            }
        ]
    return text[start:end], []


def split_committed_chunks(block_body: str) -> tuple[dict[str, str], list[str]]:
    """Per-surface chunks keyed by id, plus the ids that appear more than once.

    Duplicates are returned rather than silently last-wins: two blocks for the
    same surface is a copy-paste during a hand-edit, and the one that survives a
    dict update is whichever came second — an arbitrary winner over a note whose
    two answers disagree.
    """
    chunks: dict[str, str] = {}
    duplicates: list[str] = []
    current: str | None = None
    lines: list[str] = []
    for line in block_body.splitlines():
        match = _SURFACE_MARK_RE.match(line.strip())
        if match:
            if current is not None:
                chunks[current] = _normalized("\n".join(lines))
            current = match.group(1)
            if current in chunks:
                duplicates.append(current)
            lines = [line.strip()]
            continue
        if current is not None:
            lines.append(line)
    if current is not None:
        chunks[current] = _normalized("\n".join(lines))
    return chunks, sorted(set(duplicates))


def _chunk_json(chunk: str) -> dict[str, object] | None:
    """The chunk body parsed back when it was rendered as one JSON line."""
    for line in chunk.splitlines():
        stripped = line.strip()
        if stripped.startswith("{") and stripped.endswith("}"):
            try:
                parsed = json.loads(stripped)
            except ValueError:
                return None
            return parsed if isinstance(parsed, dict) else None
    return None


def _count_in_chunk(chunk: str) -> int | None:
    for line in chunk.splitlines():
        stripped = line.strip()
        if stripped.startswith("count:"):
            try:
                return int(stripped.split(":", 1)[1].strip())
            except ValueError:
                return None
    payload = _chunk_json(chunk)
    count = payload.get("count") if payload else None
    return count if isinstance(count, int) else None


def _chunk_items(chunk: str) -> list[str]:
    """The `items:` list a committed chunk carries, for same-count comparison."""
    items: list[str] = []
    collecting = False
    for line in chunk.splitlines():
        stripped = line.strip()
        if stripped.startswith("items:"):
            collecting = stripped == "items:"
            continue
        if collecting:
            if stripped.startswith("- "):
                items.append(stripped[2:].strip())
            elif stripped:
                break
    if items:
        return items
    payload = _chunk_json(chunk)
    raw = payload.get("items") if payload else None
    return [str(item) for item in raw] if isinstance(raw, list) else []


def _direction(committed: int | None, derived: int) -> str:
    if committed is None:
        return "contradiction"
    if committed > derived:
        return "over-claim"
    if committed < derived:
        return "under-claim"
    return "contradiction"


def _chunk_direction(chunk: str, entry: dict[str, object]) -> str:
    """Direction for a disagreeing chunk, using items when counts agree.

    A hand-edit that swaps one entry of `items:` for a fabricated one leaves
    `count:` untouched, and a count-only comparison calls that a `contradiction`
    — so `over_claim_count` read 0 over a note that names a surface the tree does
    not have. Publish refused either way; the REPORT was wrong about the one
    direction the release contract singles out.
    """
    committed_count = _count_in_chunk(chunk)
    derived_count = int(entry["count"])
    if committed_count != derived_count:
        return _direction(committed_count, derived_count)
    derived_items = {str(item) for item in entry["items"]}
    if set(_chunk_items(chunk)) - derived_items:
        return "over-claim"
    return "contradiction"


def _block_findings(text: str, derived_surfaces: list[dict[str, object]]) -> list[dict[str, object]]:
    body, structural = extract_block_body(text)
    if body is None:
        return structural
    committed, duplicates = split_committed_chunks(body)
    findings: list[dict[str, object]] = [
        {
            "kind": "duplicate-surface-block",
            "direction": "unresolvable",
            "surface": surface_id,
            "detail": f"surface `{surface_id}` is described more than once in the derived block.",
        }
        for surface_id in duplicates
    ]
    derived_by_id = {str(entry["id"]): entry for entry in derived_surfaces}
    for surface_id, entry in derived_by_id.items():
        expected = _normalized(render_surface_chunk(entry))
        if surface_id not in committed:
            findings.append(
                {
                    "kind": "surface-omitted",
                    "direction": "under-claim",
                    "surface": surface_id,
                    "detail": (
                        f"the tree derives surface `{surface_id}` and the notes do not describe it. "
                        f"Derived answer: count={entry['count']}."
                    ),
                }
            )
            continue
        if committed[surface_id] != expected:
            findings.append(
                {
                    "kind": "surface-disagrees",
                    "direction": _chunk_direction(committed[surface_id], entry),
                    "surface": surface_id,
                    "detail": (
                        f"the notes' block for `{surface_id}` disagrees with the tree "
                        f"(notes count={_count_in_chunk(committed[surface_id])}, tree count={entry['count']}). "
                        f"Question: {entry['question']}."
                    ),
                }
            )
    for surface_id in sorted(set(committed) - set(derived_by_id)):
        findings.append(
            {
                "kind": "surface-unknown",
                "direction": "over-claim",
                "surface": surface_id,
                "detail": (
                    f"the notes describe surface `{surface_id}`, which nothing in this tree derives. "
                    "It was renamed, removed, or invented."
                ),
            }
        )
    return findings


def _unresolvable(kind: str, surface_id: str, line_no: int, detail: str) -> dict[str, object]:
    """A marker nothing can be checked against.

    Separate from a mismatch, and separate from each other's construction: both
    unresolvable cases below build the identical five-key dict, and a second copy
    is where `direction` gets typed as `over-claim` and a typo starts reading as
    a tree contradiction.
    """
    return {"kind": kind, "direction": "unresolvable", "surface": surface_id, "line": line_no, "detail": detail}


def _marker_findings(text: str, derived_surfaces: list[dict[str, object]]) -> list[dict[str, object]]:
    derived_by_id = {str(entry["id"]): entry for entry in derived_surfaces}
    findings: list[dict[str, object]] = []
    for line_no, line in enumerate(text.splitlines(), start=1):
        for surface_id, field, asserted in CLAIM_MARKER_RE.findall(line):
            entry = derived_by_id.get(surface_id)
            if entry is None:
                findings.append(
                    _unresolvable(
                        "marker-unknown-surface",
                        surface_id,
                        line_no,
                        f"line {line_no} claims surface `{surface_id}`, which this tree does not derive. "
                        f"Known surfaces: {list(derived_by_id)}.",
                    )
                )
                continue
            actual = surface_field(entry, field)
            if actual is None:
                findings.append(
                    _unresolvable(
                        "marker-unknown-field",
                        surface_id,
                        line_no,
                        f"line {line_no} claims `{surface_id}.{field}`, which is not a renderable field. "
                        f"Renderable fields: {list(RENDERABLE_FIELDS)}.",
                    )
                )
                continue
            if asserted.strip() != actual:
                committed_count = None
                if field == "count":
                    try:
                        committed_count = int(asserted.strip())
                    except ValueError:
                        committed_count = None
                findings.append(
                    {
                        "kind": "marker-disagrees",
                        "direction": (
                            _direction(committed_count, int(entry["count"])) if field == "count" else "contradiction"
                        ),
                        "surface": surface_id,
                        "line": line_no,
                        "detail": (
                            f"line {line_no} claims `{surface_id}.{field}` is `{asserted.strip()}`; "
                            f"the tree says `{actual}`. Question: {entry['question']}."
                        ),
                    }
                )
    return findings


def audit_notes_text(text: str, derived_surfaces: list[dict[str, object]]) -> list[dict[str, object]]:
    """Every disagreement between ``text`` and a fresh derivation."""
    return [*_block_findings(text, derived_surfaces), *_marker_findings(text, derived_surfaces)]


def audit_notes_file(
    path: Path,
    repo_root: Path,
    *,
    require_git: bool = False,
    tracked_tree=None,
) -> list[dict[str, object]]:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        return [
            {
                "kind": "notes-unreadable",
                "direction": "unresolvable",
                "surface": None,
                "detail": f"could not read the notes file `{path}`: {exc}",
            }
        ]
    return audit_notes_text(
        text,
        derive_surfaces(repo_root, require_git=require_git, tracked_tree=tracked_tree),
    )


def finding_lines(findings: list[dict[str, object]]) -> list[str]:
    return [f"[{finding['direction']}] {finding['kind']}: {finding['detail']}" for finding in findings]
