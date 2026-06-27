#!/usr/bin/env python3
"""Reviewed-fixable duplicate classification overlay for the boy-scout dup ratchet (item 5).

The two nose advisories (``inventory_nose_clones.py`` for code,
``inventory_doc_duplicates.py`` for docs) report RAW clone families, including
intentional portable boilerplate. The ratchet (slice 2) acts only on a REVIEWED
``fixable`` subset, so this layer records a classification overlay keyed by family
identity: the offset/path-independent ``family_fingerprint`` for code (slice 4 re-key,
in lockstep with the gate/advisory baselines — was nose's ``family_id``) and
``family_signature`` for docs.

Design (slice 1):

- **Classified-only overlay.** The artifact stores ONLY explicitly-classified
  families (``intentional`` / ``fixable``); an unlisted family defaults to
  ``unreviewed``. The two existing baselines own drift detection; this overlay
  owns fixable classification, so it stays small and churn-free.
- **Auto-seed is conservative.** A family whose every member file is a portable
  per-skill copy (``resolve_adapter.py`` / ``init_adapter.py``) seeds
  ``intentional``; everything else stays ``unreviewed`` (not stored). Slice 1
  NEVER auto-seeds ``fixable`` — that is an operator-confirmed decision (the gate
  and the structural-field proposal UX are slice 2).
- **Existing classifications are authoritative.** A merge preserves every prior
  entry and only ADDS new auto-``intentional`` entries; it never downgrades or
  drops operator review.
- **``fixable_ceiling`` is the count of ``fixable`` entries** (0 after a fresh
  seed). The one-way-decrease lock-in is enforced by the slice-2 gate, not here.
"""

from __future__ import annotations

from typing import Any, Iterable

SCHEMA_VERSION = "charness.quality.dup_review.v1"
SURFACES = ("code", "doc")
CLASSES = ("fixable", "intentional", "unreviewed")
PORTABLE_COPY_BASENAMES = ("resolve_adapter.py", "init_adapter.py")
DEFAULT_NOTE = (
    "Reviewed fixable-duplication overlay (item 5). Keyed by family identity "
    "(code: offset/path-independent content fingerprint; doc: family_signature). Stores only explicitly-"
    "classified families; an unlisted family defaults to 'unreviewed'. "
    "fixable_ceiling (count of 'fixable') is one-way and only decreases via a "
    "deliberate re-review. nose-baseline.json / doc-nose-baseline.json own drift "
    "detection; this overlay owns fixable classification."
)


def _basename(path: str) -> str:
    return str(path).replace("\\", "/").rsplit("/", 1)[-1]


def classify(member_files: Iterable[str], portable_basenames: Iterable[str] = PORTABLE_COPY_BASENAMES) -> str:
    """A family whose every member file is a portable per-skill copy is
    ``intentional``; otherwise ``unreviewed``. An empty member set is
    ``unreviewed`` (nothing to claim). Never returns ``fixable`` — slice 1 does
    not auto-confirm fixable duplication."""
    files = [f for f in member_files if f]
    portable = set(portable_basenames)
    if files and all(_basename(f) in portable for f in files):
        return "intentional"
    return "unreviewed"


def _code_member_files(family: dict[str, Any]) -> list[str]:
    locations = family.get("sample_locations") or []
    return [loc.get("file") for loc in locations if isinstance(loc, dict) and loc.get("file")]


def family_records(
    code_families: Iterable[dict[str, Any]], doc_families: Iterable[dict[str, Any]]
) -> list[tuple[str, str, list[str]]]:
    """Normalize both inventories into ``(surface, identity, member_files)`` rows.

    Code identity is the offset/path-independent ``family_fingerprint`` (slice 4 re-key,
    in lockstep with the gate/advisory baselines — was nose's ``family_id``); doc identity
    is ``signature``. Doc families expose no clean per-member paths (only witness spans), so
    they carry no member files and therefore never auto-seed ``intentional`` in slice 1."""
    records: list[tuple[str, str, list[str]]] = []
    for family in code_families:
        fingerprint = family.get("family_fingerprint")
        if isinstance(fingerprint, str) and fingerprint:
            records.append(("code", fingerprint, _code_member_files(family)))
    for family in doc_families:
        signature = family.get("signature")
        if isinstance(signature, str) and signature:
            records.append(("doc", signature, []))
    return records


def build_review(
    existing: dict[str, Any] | None,
    code_families: Iterable[dict[str, Any]],
    doc_families: Iterable[dict[str, Any]],
    *,
    reviewed_at: str,
    portable_basenames: Iterable[str] = PORTABLE_COPY_BASENAMES,
    note: str = DEFAULT_NOTE,
) -> dict[str, Any]:
    """Merge auto-seeded ``intentional`` classifications into an existing overlay.

    Preserves every existing entry (operator classifications are authoritative)
    and only ADDS new auto-``intentional`` entries for newly-seen portable-copy
    families. ``fixable_ceiling`` = count of ``fixable`` entries."""
    by_key: dict[tuple[str, str], dict[str, Any]] = {
        (entry["surface"], entry["id"]): dict(entry)
        for entry in ((existing or {}).get("entries") or [])
        if isinstance(entry, dict) and entry.get("surface") and entry.get("id")
    }
    for surface, identity, member_files in family_records(code_families, doc_families):
        key = (surface, identity)
        if key in by_key:
            continue  # existing classification wins
        if classify(member_files, portable_basenames) == "intentional":
            by_key[key] = {
                "id": identity,
                "surface": surface,
                "class": "intentional",
                "note": "auto-seeded: portable per-skill copy",
                "reviewed_at": reviewed_at,
            }
    entries = sorted(by_key.values(), key=lambda entry: (entry["surface"], entry["id"]))
    fixable_ceiling = sum(1 for entry in entries if entry.get("class") == "fixable")
    return {
        "schemaVersion": SCHEMA_VERSION,
        "note": note,
        "fixable_ceiling": fixable_ceiling,
        "entries": entries,
    }


def validate_review(review: Any) -> list[str]:
    """Return a list of schema errors (empty when the overlay is well-formed)."""
    errors: list[str] = []
    if not isinstance(review, dict):
        return ["review must be a JSON object"]
    if review.get("schemaVersion") != SCHEMA_VERSION:
        errors.append(f"schemaVersion must be {SCHEMA_VERSION!r}")
    entries = review.get("entries")
    if not isinstance(entries, list):
        return errors + ["entries must be a list"]
    seen: set[tuple[str, str]] = set()
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            errors.append(f"entry {index} must be an object")
            continue
        surface, identity, klass = entry.get("surface"), entry.get("id"), entry.get("class")
        if surface not in SURFACES:
            errors.append(f"entry {index}: surface must be one of {SURFACES}")
        if not isinstance(identity, str) or not identity:
            errors.append(f"entry {index}: id must be a non-empty string")
        if klass not in CLASSES:
            errors.append(f"entry {index}: class must be one of {CLASSES}")
        if not isinstance(entry.get("note"), str):
            errors.append(f"entry {index}: note must be a string")
        if not isinstance(entry.get("reviewed_at"), str):
            errors.append(f"entry {index}: reviewed_at must be a string")
        if isinstance(surface, str) and isinstance(identity, str):
            if (surface, identity) in seen:
                errors.append(f"entry {index}: duplicate (surface, id) = ({surface}, {identity})")
            seen.add((surface, identity))
    ceiling = review.get("fixable_ceiling")
    fixable = sum(1 for entry in entries if isinstance(entry, dict) and entry.get("class") == "fixable")
    if ceiling != fixable:
        errors.append(f"fixable_ceiling ({ceiling!r}) must equal the count of 'fixable' entries ({fixable})")
    return errors
