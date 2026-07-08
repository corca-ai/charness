#!/usr/bin/env python3
"""Gate-baseline schema (dup-ratchet-baseline.json) — build/load/validate (item 5, slice D).

Split out of ``dup_ratchet_lib`` (module-length split, mirroring the ``nose_report_lib``
/ ``nose_baseline_lib`` and ``check_dup_ratchet`` / ``dup_ratchet_scan`` splits): the
accepted-baseline schema is its own concern from the two-arm policy (``evaluate``) and
the overlay/scoped-rebaseline seams that remain in ``dup_ratchet_lib``.

Schema v3 (``charness.quality.dup_ratchet_baseline.v3``) stores each accepted family as
``{"fingerprint": str, "member_hashes": [str, ...]}`` under ``code_families`` (sorted by
fingerprint; each family's ``member_hashes`` sorted, duplicate-preserving) — replacing
v2's bare ``code_family_fingerprints`` list. The per-family member hashes are the new
information schema v3 adds: they let the CLI's ``dup_ratchet_lib.classify_reductions``
pre-pass recognize a vanished family's member multiset properly containing a
candidate-new family's as a membership REDUCTION (advisory), before
``dup_ratchet_lib.evaluate`` ever sees the (still pure, still opaque-string) fingerprint
diff. The loaders read ONLY the v3 shape: a v2 (or older) baseline has no
``code_families`` key and reads as ``None`` — the same no-dual-read degrade-to-advisory
discipline as the v1->v2 move (a stale checkout must not misread an old shape)."""

from __future__ import annotations

from typing import Any, Iterable, Mapping

GATE_BASELINE_SCHEMA_VERSION = "charness.quality.dup_ratchet_baseline.v3"
GATE_BASELINE_NOTE = (
    "Accepted code clone content fingerprints for the boy-scout dup ratchet (item 5, slice 4+D). "
    "A code family fingerprint present now but absent here (and not 'intentional' in dup-review.json) "
    "is a NEW fixable-eligible family and hard-blocks. Keyed by a gate-computed, offset/path-"
    "INDEPENDENT content fingerprint (sha256 over the sorted, duplicate-preserving normalized member "
    "spans; see nose_fingerprint_lib) from a FULL `nose query` over the scope — NOT nose's offset/path-"
    "folding family_id (slice 4 re-key, resolving deferred decision D30). Schema v3 stores each accepted "
    "family as {fingerprint, member_hashes} (`code_families`, sorted list) rather than a bare fingerprint "
    "list: the per-family member hashes let the CLI classify a membership REDUCTION (a vanished family's "
    "member multiset properly containing a candidate-new family's) as advisory, not a hard block, before "
    "evaluate() ever sees it. CHURN CAVEAT: the fingerprint is STABLE across pure line-shifts (inserting "
    "lines above an unchanged span no longer rotates it) and, under algo v2, across an in-place comment "
    "or internal-whitespace edit inside a Python span (falls back to v1 rstrip-only per member on any "
    "tokenize failure); incidental member-file edits do not force a re-baseline. Re-baseline deliberately "
    "on: a reviewed new/changed family, a genuine membership change NOT classified as a reduction, a "
    "nose-version bump that regroups families, OR a fingerprint_algo_version bump. The baseline stamps "
    "the producing nose tool_version AND fingerprint_algo_version; the gate WARNS (never degrades) on "
    "either skew, so a silent bump's drift reads as re-baseline, not new dup. Docs key on the "
    "doc-nose-baseline signature."
)


def build_gate_baseline(
    code_families: Mapping[str, Iterable[str]],
    *,
    tool_version: str = "",
    algo_version: str = "",
    note: str = GATE_BASELINE_NOTE,
) -> dict[str, Any]:
    """Build a schema-v3 gate baseline from a ``{fingerprint: member_hashes}`` map.
    Each family's member hashes are sorted (duplicate-preserving); families are
    sorted by fingerprint for a deterministic, diff-friendly file."""
    families = sorted(
        (
            {"fingerprint": str(fid), "member_hashes": sorted(str(h) for h in hashes)}
            for fid, hashes in code_families.items()
            if fid
        ),
        key=lambda entry: entry["fingerprint"],
    )
    baseline: dict[str, Any] = {
        "schemaVersion": GATE_BASELINE_SCHEMA_VERSION,
        "note": note,
        "code_families": families,
    }
    # Stamp only when known so a legacy write stays unstamped, never a false skew.
    if tool_version:
        baseline["tool_version"] = str(tool_version)
    if algo_version:
        baseline["fingerprint_algo_version"] = str(algo_version)
    return baseline


def _iter_gate_baseline_families(data: Any) -> list[dict[str, Any]] | None:
    """Shared v3-shape reader: the ``code_families`` list, or ``None`` when the file
    is absent/unreadable/malformed OR keyed by a pre-v3 baseline (legacy
    ``code_family_fingerprints`` / ``code_family_ids``) — no dual-read, same degrade
    discipline as the v1->v2 move: a stale checkout must not misread an old shape."""
    if not isinstance(data, dict):
        return None
    families = data.get("code_families")
    if not isinstance(families, list):
        return None
    return families


def load_gate_baseline_ids(data: Any) -> set[str] | None:
    """Return the accepted code fingerprint set, or ``None`` when absent/unreadable/
    malformed/legacy (FD8 degrade). The function name stays identity-agnostic ("the
    accepted identity set"); only the shape it reads changed (v3: per-family
    ``{fingerprint, member_hashes}`` objects, not a bare fingerprint list)."""
    families = _iter_gate_baseline_families(data)
    if families is None:
        return None
    ids: set[str] = set()
    for entry in families:
        if not isinstance(entry, dict):
            return None
        fingerprint = entry.get("fingerprint")
        if isinstance(fingerprint, str) and fingerprint:
            ids.add(fingerprint)
    return ids


def load_gate_baseline_members(data: Any) -> dict[str, list[str]] | None:
    """Return ``{fingerprint: member_hashes}`` for every accepted family, or ``None``
    on the same absent/unreadable/malformed/legacy conditions as
    ``load_gate_baseline_ids``. The CLI's reduction pre-pass (``classify_reductions``)
    consumes this to compare a vanished family's member multiset against a
    candidate-new family's."""
    families = _iter_gate_baseline_families(data)
    if families is None:
        return None
    members: dict[str, list[str]] = {}
    for entry in families:
        if not isinstance(entry, dict):
            return None
        fingerprint = entry.get("fingerprint")
        hashes = entry.get("member_hashes")
        if not isinstance(fingerprint, str) or not fingerprint or not isinstance(hashes, list):
            return None
        members[fingerprint] = [str(h) for h in hashes]
    return members


def _baseline_string_field(data: Any, key: str) -> str:
    """A stamped string field from the gate baseline, or ``""`` when absent/legacy."""
    if isinstance(data, dict):
        value = data.get(key)
        if isinstance(value, str):
            return value
    return ""


def load_gate_baseline_tool_version(data: Any) -> str:
    """The nose version stamped into the gate baseline, or ``""`` when absent/legacy.
    The gate compares it against the live scan version and surfaces a skew WARNING
    (never a degrade): a nose bump can regroup families and drift the fingerprint set,
    so the operator must read "re-baseline", not "remove duplication"."""
    return _baseline_string_field(data, "tool_version")


def load_gate_baseline_algo_version(data: Any) -> str:
    """The fingerprint algorithm version stamped into the gate baseline, or ``""`` when
    absent/legacy. A future normalization change (e.g. landing token/comment-aware
    normalization) bumps the algo version; the gate then WARNS (never degrades) so the
    drifted fingerprints read as re-baseline, not a corpus-wide false hard-block."""
    return _baseline_string_field(data, "fingerprint_algo_version")


def algo_version_skew(baseline_algo: str | None, live_algo: str | None) -> str | None:
    """Operator warning when the stored fingerprints were minted under a different
    fingerprint algorithm version than the one now computing, else ``None``. A MISSING
    stamp on either side returns ``None`` (unknown, not a mismatch). Mirrors
    ``nose_report_lib.tool_version_skew`` for the gate-owned identity axis."""
    base = str(baseline_algo or "").strip()
    live = str(live_algo or "").strip()
    if base and live and base != live:
        return (
            f"fingerprint algo skew: baseline written under algo v{base}, now computing "
            f"with algo v{live}. The content-fingerprint normalization changed, so a "
            "re-baseline (--write-baseline) is the honest fix — do NOT treat the rotated "
            "fingerprints as new duplication."
        )
    return None


def validate_gate_baseline(data: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["gate baseline must be a JSON object"]
    if data.get("schemaVersion") != GATE_BASELINE_SCHEMA_VERSION:
        errors.append(f"schemaVersion must be {GATE_BASELINE_SCHEMA_VERSION!r}")
    version = data.get("tool_version")
    if version is not None and not isinstance(version, str):
        errors.append("tool_version must be a string when present")
    algo = data.get("fingerprint_algo_version")
    if algo is not None and not isinstance(algo, str):
        errors.append("fingerprint_algo_version must be a string when present")
    families = data.get("code_families")
    if not isinstance(families, list):
        errors.append("code_families must be a list")
        return errors
    for index, entry in enumerate(families):
        if not isinstance(entry, dict):
            errors.append(f"code_families[{index}] must be an object")
            continue
        fingerprint = entry.get("fingerprint")
        if not isinstance(fingerprint, str) or not fingerprint:
            errors.append(f"code_families[{index}].fingerprint must be a non-empty string")
        hashes = entry.get("member_hashes")
        if not isinstance(hashes, list) or not hashes:
            errors.append(f"code_families[{index}].member_hashes must be a non-empty list")
        else:
            for hash_index, member_hash in enumerate(hashes):
                if not isinstance(member_hash, str) or not member_hash:
                    errors.append(
                        f"code_families[{index}].member_hashes[{hash_index}] must be a non-empty string"
                    )
    return errors
