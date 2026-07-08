#!/usr/bin/env python3
"""Pure planning functions for the dup-fingerprint algo migration tool (item 5, slice D).

``migrate_dup_fingerprints.py`` is a REUSABLE tool: this class of migration recurs
every time ``nose_fingerprint_lib.FINGERPRINT_ALGO_VERSION`` bumps (the v1->v2
token-aware-normalization landing is only the first instance). Given a live scan
already enriched with BOTH the old and new algo's identity per family
(``{"v1": ..., "v2": ..., "member_hashes": [...], "nose_id": ...}``) and the
pre-migration artifacts, these pure functions plan the v1->v2 remap for the three
surfaces the migration touches: the gate baseline, the advisory baseline, and the
dup-review overlay. No file I/O and no nose invocation here -- ``migrate_dup_fingerprints.py``
is the I/O shell (adapter load, nose scan, file read/write, CLI, dry-run/--execute)."""

from __future__ import annotations

from typing import Any, Iterable


def collision_report(enriched: list[dict[str, Any]]) -> dict[str, Any]:
    """The one-shot collision assertion: distinct v2 fingerprints must equal
    distinct nose family ids over the live scan. This guards an IMPLEMENTATION-
    induced collision (e.g. an accidental set()-dedup) -- PQ1 already precludes a
    NATURAL collision under nose's global clustering, so ``ok: False`` here means
    the migration tool (or the fingerprint algo) has a bug, not that the corpus is
    unlucky; the caller must refuse to migrate on a failed assertion."""
    v2_fingerprints = {entry["v2"] for entry in enriched}
    nose_ids = {entry["nose_id"] for entry in enriched if entry.get("nose_id")}
    return {
        "distinct_v2_fingerprints": len(v2_fingerprints),
        "distinct_nose_family_ids": len(nose_ids),
        "ok": len(v2_fingerprints) == len(nose_ids),
    }


def plan_gate_baseline_migration(
    old_ids: set[str],
    enriched: list[dict[str, Any]],
    accept_new_families: Iterable[str],
) -> dict[str, Any]:
    """Remap the gate baseline (schema v3: fingerprint + member_hashes per family).

    A SURVIVOR (an old v1 id found in the live scan) moves to its live v2
    fingerprint + member hashes. A VANISHED old id (absent from the live scan) is
    dropped. A live family whose v1 id was NOT previously accepted is a
    ``requires_review`` candidate and is EXCLUDED from the new baseline unless its
    v2 fingerprint is named via ``accept_new_families`` -- goal-introduced
    duplication must not be silently absorbed into "accepted" by a routine algo
    migration."""
    by_v1 = {entry["v1"]: entry for entry in enriched}
    accept = set(accept_new_families)
    survivors = sorted(old_ids & set(by_v1))
    vanished = sorted(old_ids - set(by_v1))
    candidates = sorted(entry["v2"] for entry in enriched if entry["v1"] not in old_ids)
    accepted_new = sorted(set(candidates) & accept)
    requires_review = sorted(set(candidates) - accept)
    new_members: dict[str, list[str]] = {
        by_v1[v1]["v2"]: list(by_v1[v1]["member_hashes"]) for v1 in survivors
    }
    for entry in enriched:
        if entry["v2"] in accepted_new:
            new_members[entry["v2"]] = list(entry["member_hashes"])
    return {
        "survivors": survivors, "vanished": vanished,
        "accepted_new": accepted_new, "requires_review": requires_review,
        "new_members": new_members,
    }


def plan_advisory_baseline_migration(old_ids: set[str], enriched: list[dict[str, Any]]) -> dict[str, Any]:
    """Remap the advisory baseline (schema key UNCHANGED -- only the fingerprint
    VALUES migrate). A survivor moves to its live v2 fingerprint; a vanished old id
    is dropped. New live families stay unaccepted here -- the advisory's whole point
    is reporting drift, so there is no requires_review gate on this surface; only
    the gate baseline blocks."""
    by_v1 = {entry["v1"]: entry for entry in enriched}
    survivors = sorted(old_ids & set(by_v1))
    vanished = sorted(old_ids - set(by_v1))
    new_ids = sorted({by_v1[v1]["v2"] for v1 in survivors})
    return {"survivors": survivors, "vanished": vanished, "new_ids": new_ids}


def plan_review_migration(
    entries: list[dict[str, Any]], enriched: list[dict[str, Any]]
) -> dict[str, Any]:
    """Member-preserving remap of every ``code``-surface overlay entry's ``id``
    (v1 fingerprint -> v2 fingerprint), preserving ``class``/``note``/``reviewed_at``
    VERBATIM. An entry whose v1 id is not in the live scan is DROPPED (an
    already-orphaned classification) with its id logged, never silently kept
    stale. ``doc``-surface entries pass through untouched (signature-keyed,
    unrelated to the code fingerprint algo). This is NEVER a
    ``dup_review_lib.build_review`` re-seed (S4-D8's discipline, applied
    generically): every field survives byte-for-byte except the remapped id."""
    by_v1 = {entry["v1"]: entry["v2"] for entry in enriched}
    migrated: list[dict[str, Any]] = []
    dropped_ids: list[str] = []
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        if entry.get("surface") != "code":
            migrated.append(entry)
            continue
        old_id = entry.get("id")
        new_id = by_v1.get(old_id) if isinstance(old_id, str) else None
        if new_id is None:
            dropped_ids.append(str(old_id))
            continue
        migrated.append({**entry, "id": new_id})
    return {"entries": migrated, "dropped_ids": sorted(dropped_ids)}
