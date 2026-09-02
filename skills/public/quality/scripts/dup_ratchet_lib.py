#!/usr/bin/env python3
"""Boy-scout duplicate ratchet — pure policy + gate-baseline seams (item 5, slice 2).

Slice 1 built the reviewed-fixable overlay (``dup_review_lib`` / ``dup-review.json``).
This module is the ratchet's teeth: given the current duplicate families, the
accepted baselines, and the overlay classifications, it decides whether a push
should block. It is the portable unit (a standalone gate script + payload
contract); ``check_dup_ratchet.py`` is one consumer (charness wires it into
``run-quality.sh`` + broad pre-push).

Two arms (spec Fixed Decision 1 + Slice 2 D1–D3):

- **Hard arm (always):** a NEW fixable-eligible family hard-blocks. "New" =
  present now, absent from the accepted reference, not classified ``intentional``.
  Code newness diffs the current content-fingerprint set against a gate-owned
  fingerprint baseline (``dup-ratchet-baseline.json``). The fingerprint is a
  gate-computed, offset/path-INDEPENDENT content hash of the family's member spans
  (``nose_fingerprint_lib``), NOT nose's ``family_id`` — slice 4 re-key resolving
  deferred decision D30. nose's ``family_id`` folds each member span's normalized
  content, its **line offset**, AND its **file path**, so editing any scanned member
  file — even inserting lines *above* an unchanged span — rotated the whole id and
  false-blocked the hard arm with ZERO new duplication. The content fingerprint is
  STABLE across such pure line-shifts (a member's own span bytes do not change when
  lines move around it) while still rotating on a genuine span-content change, so real
  new/changed duplication is caught with no false-negative. Re-baseline deliberately
  (``--write-baseline``) on a reviewed new family, a member-set (membership) change, a
  nose-version bump that regroups families, OR a ``fingerprint_algo_version`` bump —
  not on incidental member-file edits. Doc newness reuses the position-independent
  ``signature`` drift (``doc-nose-baseline.json``, ``path#heading``). Recording a new
  family ``unreviewed`` does NOT unblock it (D3).
- **Boy-scout arm (escalating nudge):** while ``fixable_ceiling > floor_F`` and the
  reviewed overlay has not advanced (``stagnation_commits >= escalation_K``), the
  normally-advisory "remove existing fixable dup" nudge escalates to a one-time
  block, which resets when the overlay edit advances the git anchor. At/below the
  healthy floor ``F`` the boy-scout arm is fully advisory; the hard arm still fires.

Stagnation is measured from git, not a stored counter or self-SHA (FD5): the anchor
is the commit that last touched the overlay; stagnation = ``rev-list --count
<anchor>..HEAD``. ``evaluate`` takes the stagnation distance *injected* (the git
seams live in ``dup_ratchet_git`` and are separate and injectable) so the policy
stays pure and testable.
An anchor that is not an ancestor of HEAD (rebase/squash/force-push orphaned it)
softens the boy-scout arm to advisory ("re-baseline needed"); it never blocks on a
phantom. Overlay/baseline/nose missing => degraded advisory, never a block (FD8).
"""

from __future__ import annotations

from collections import Counter
from typing import Any, Iterable


# --------------------------------------------------------------------------- #
# Overlay (dup-review.json) readers
# --------------------------------------------------------------------------- #
def overlay_intentional(overlay: dict[str, Any] | None) -> tuple[set[str], set[str]]:
    """Return ``(intentional_code_ids, intentional_doc_signatures)`` from the overlay.

    An unlisted family is implicitly ``unreviewed`` (classified-only overlay), and
    ``unreviewed``/``fixable`` do NOT suppress the hard arm — only ``intentional`` does.
    """
    code: set[str] = set()
    doc: set[str] = set()
    for entry in (overlay or {}).get("entries") or []:
        if not isinstance(entry, dict) or entry.get("class") != "intentional":
            continue
        surface, identity = entry.get("surface"), entry.get("id")
        if not isinstance(identity, str) or not identity:
            continue
        if surface == "code":
            code.add(identity)
        elif surface == "doc":
            doc.add(identity)
    return code, doc


def overlay_fixable_ceiling(overlay: dict[str, Any] | None) -> int:
    value = (overlay or {}).get("fixable_ceiling")
    return value if isinstance(value, int) and not isinstance(value, bool) else 0


# --------------------------------------------------------------------------- #
# Scope coverage (slice 4: gate by property, not by enumeration)
#
# scope_paths is a scan-cost boundary, not a duplication-eligibility boundary --
# nothing outside it ever gets a family FORMED at all. Nothing previously said so,
# or how much that left out. HOW TO SIZE the uncovered population, stated as the
# method rather than as any run's answer: read this run's own git-tracked file
# list (the population scope_paths is drawn against) and subtract whatever falls
# under one of scope_paths' own entries, compared by path SEGMENT so a
# same-prefix sibling directory is never miscounted as covered. The count is
# computed fresh every run from that live tracked-file list; it is never frozen
# here.
# --------------------------------------------------------------------------- #
# --------------------------------------------------------------------------- #
# Reduction pre-pass (S4-Defer-3: membership-shrink is advisory, not a hard block)
#
# The gate-baseline schema (build/load/validate ``dup-ratchet-baseline.json``) lives
# in the sibling ``dup_ratchet_baseline_lib`` module (length-cap split). This function
# is a PURE CLI-layer pre-pass that runs BEFORE ``evaluate`` and never touches it
# (S4-D9 keeps ``evaluate``'s opaque-string set-diff signature untouched, protecting
# the ~15 existing policy tests): a candidate-new family whose member multiset is a
# PROPER sub-multiset of a vanished baseline family's is a membership REDUCTION (a
# copy was removed), not new duplication, so the CLI advises instead of hard-blocking.
# --------------------------------------------------------------------------- #
def classify_reductions(
    live_members: dict[str, list[str]],
    baseline_members: dict[str, list[str]],
    candidate_new: Iterable[str],
) -> list[dict[str, str]]:
    """Classify each ``candidate_new`` fingerprint as a membership reduction of some
    vanished baseline family, or leave it unclassified (genuine new duplication).

    ``vanished`` = baseline fingerprints absent from ``live_members`` (the family the
    candidate might be a shrunk remainder of). A candidate is a reduction of a
    vanished family when its member-hash multiset (``collections.Counter``) is a
    PROPER sub-multiset of the vanished family's (every count <= , and a strictly
    smaller total — not merely equal). Pairing is deterministic: the smallest
    vanished superset by member count, then by fingerprint, so the result never
    depends on dict iteration order. A candidate absent from ``live_members`` (should
    not happen; the CLI only asks about fingerprints it just scanned) is left
    unclassified, never an error — this stays a pure best-effort classifier, never a crash."""
    vanished = {fp: hashes for fp, hashes in baseline_members.items() if fp not in live_members}
    reductions: list[dict[str, str]] = []
    for new_fingerprint in sorted(candidate_new):
        live_hashes = live_members.get(new_fingerprint)
        if live_hashes is None:
            continue
        live_counter = Counter(live_hashes)
        live_total = sum(live_counter.values())
        best: tuple[int, str] | None = None
        for old_fingerprint, old_hashes in vanished.items():
            old_counter = Counter(old_hashes)
            old_total = sum(old_counter.values())
            if old_total <= live_total:
                continue  # not strictly smaller -> not a proper sub-multiset
            if any(count > old_counter.get(member, 0) for member, count in live_counter.items()):
                continue  # some member over-represented -> not a sub-multiset
            key = (old_total, old_fingerprint)
            if best is None or key < best:
                best = key
        if best is not None:
            reductions.append({"new_fingerprint": new_fingerprint, "old_fingerprint": best[1]})
    return reductions


# --------------------------------------------------------------------------- #
# Scoped re-baseline (routine rotation churn — never a silent full-corpus accept)
# --------------------------------------------------------------------------- #
def parse_rotations(raw_rotations: list[str]) -> tuple[list[tuple[str, str]], list[str]]:
    """Parse repeated ``OLD_ID=NEW_ID`` strings. Returns ``(pairs, malformed_raw)``."""
    pairs: list[tuple[str, str]] = []
    malformed: list[str] = []
    for raw in raw_rotations:
        old_id, sep, new_id = raw.partition("=")
        old_id, new_id = old_id.strip(), new_id.strip()
        if not sep or not old_id or not new_id:
            malformed.append(raw)
            continue
        pairs.append((old_id, new_id))
    return pairs, malformed


def scoped_rebaseline_exemptions(
    *,
    live_members: dict[str, list[str]],
    existing_members: dict[str, list[str]],
    overlay: dict[str, Any] | None,
    named_new_ids: set[str],
) -> dict[str, Any]:
    """Evaluate-parity universe trim for the scoped re-baseline: the gate's evaluate
    path never blocks on overlay-``intentional`` families or membership reductions,
    so a scoped accept must not refuse them as "unnamed new" either — otherwise the
    exact rotations the evaluator suggests are un-acceptable whenever tolerated
    families are live. Returns the ``exempt_live_ids`` refusal exclusion plus the
    ``ignored_intentional`` / ``unnamed_reductions`` evidence and one advisory line
    per exemption class (never silent). Exempt ids are left OUT of the baseline:
    intentional families are owned by the review overlay, and an unrotated reduction
    keeps its vanished old family until the operator names the rotation."""
    live_ids, existing_ids = set(live_members), set(existing_members)
    intentional_code, _doc = overlay_intentional(overlay)
    candidate_new = live_ids - existing_ids - intentional_code
    reductions = classify_reductions(live_members, existing_members, candidate_new)
    unnamed_reductions = [r for r in reductions if r["new_fingerprint"] not in named_new_ids]
    ignored_intentional = sorted((live_ids - existing_ids) & intentional_code - named_new_ids)
    advisories = [
        f"ADVISORY (reduction): family {r['old_fingerprint']} shrank to {r['new_fingerprint']} "
        f"(membership reduction, not new duplication); left out of the baseline (old id kept) — "
        f"accept with --accept-rotation {r['old_fingerprint']}={r['new_fingerprint']}"
        for r in unnamed_reductions
    ]
    if ignored_intentional:
        advisories.append(
            "ADVISORY (intentional): left overlay-intentional live family(ies) out of the "
            "baseline by design (the dup-review overlay owns them; no action needed): "
            + ", ".join(ignored_intentional)
        )
    return {
        "exempt_live_ids": set(ignored_intentional)
        | {r["new_fingerprint"] for r in unnamed_reductions},
        "ignored_intentional": ignored_intentional,
        "unnamed_reductions": unnamed_reductions,
        "advisories": advisories,
    }


def plan_scoped_rebaseline(
    *,
    existing_ids: set[str],
    live_ids: set[str],
    rotations: list[tuple[str, str]],
    accept_families: list[str],
    exempt_live_ids: set[str] = frozenset(),
) -> dict[str, Any]:
    """Pure planner for a scoped re-baseline: apply ONLY the named rotation pairs
    and named new-family accepts onto ``existing_ids``, and refuse (never silently
    absorb) any other delta between ``live_ids`` and the result. This is the teeth
    fix for ``--write-baseline``'s full-scan overwrite, which re-accepts every
    unreviewed new family wholesale on routine rotation churn. Returns ``ok`` plus
    either ``updated_ids`` (the new accepted set) or ``errors``/``refused_added``.
    ``exempt_live_ids`` are live ids the gate's evaluate path already
    tolerates (overlay-intentional families, membership reductions): they are
    neither refused nor absorbed, so both paths judge the same family universe
    (given readable overlay/baseline inputs).
    """
    errors: list[str] = []
    seen_old: set[str] = set()
    for old_id, new_id in rotations:
        if old_id in seen_old:
            errors.append(f"--accept-rotation names {old_id!r} more than once")
        seen_old.add(old_id)
        if old_id not in existing_ids:
            errors.append(f"--accept-rotation OLD_ID {old_id!r} is not in the current baseline")
        if new_id not in live_ids:
            errors.append(f"--accept-rotation NEW_ID {new_id!r} is not in the live scan")
    for family_id in accept_families:
        if family_id not in live_ids:
            errors.append(f"--accept-family {family_id!r} is not in the live scan")
        elif family_id in existing_ids:
            errors.append(f"--accept-family {family_id!r} is already in the baseline")
    if errors:
        return {"ok": False, "errors": errors, "refused_added": [], "updated_ids": None}

    updated_ids = set(existing_ids)
    for old_id, new_id in rotations:
        updated_ids.discard(old_id)
        updated_ids.add(new_id)
    updated_ids.update(accept_families)

    refused_added = sorted(live_ids - updated_ids - set(exempt_live_ids))
    if refused_added:
        return {"ok": False, "errors": [], "refused_added": refused_added, "updated_ids": None}
    return {"ok": True, "errors": [], "refused_added": [], "updated_ids": updated_ids}


# --------------------------------------------------------------------------- #
# Policy
# --------------------------------------------------------------------------- #
def _boy_scout_arm(
    *,
    above_floor: bool,
    anchor: str | None,
    anchor_is_ancestor: bool,
    stagnation: int | None,
    escalation_K: int,
) -> tuple[bool, str]:
    """Return ``(block, status)`` for the boy-scout arm. Block only when above the
    floor, the anchor is a live ancestor, and stagnation has reached K."""
    if not above_floor:
        return False, "below-floor-advisory"
    if not anchor or not anchor_is_ancestor:
        return False, "anchor-not-ancestor-advisory"
    if stagnation is not None and stagnation >= escalation_K:
        return True, "boy-scout-escalation-block"
    return False, "boy-scout-advisory"


def evaluate(
    *,
    code_family_ids: Iterable[str],
    gate_baseline_ids: Iterable[str],
    doc_drift_signatures: Iterable[str],
    intentional_code_ids: Iterable[str],
    intentional_doc_signatures: Iterable[str],
    fixable_ceiling: int,
    floor_F: int,
    escalation_K: int,
    stagnation: int | None,
    anchor: str | None,
    anchor_is_ancestor: bool,
    degraded_reasons: Iterable[str] | None = None,
) -> dict[str, Any]:
    """Decide the ratchet verdict. ``ok``/``block`` are the top-level result; the
    component booleans (``hard_block``, ``boy_scout_block``, ``above_floor``) and the
    new-family lists make the decision auditable and the acceptance tests precise."""
    degraded = [str(reason) for reason in (degraded_reasons or [])]
    new_code = sorted(set(code_family_ids) - set(gate_baseline_ids) - set(intentional_code_ids))
    new_doc = sorted(set(doc_drift_signatures) - set(intentional_doc_signatures))

    verdict: dict[str, Any] = {
        "new_code_families": new_code,
        "new_doc_families": new_doc,
        "fixable_ceiling": fixable_ceiling,
        "floor_F": floor_F,
        "escalation_K": escalation_K,
        "stagnation": stagnation,
        "anchor": anchor,
        "anchor_is_ancestor": bool(anchor_is_ancestor),
        "degraded_reasons": degraded,
        # The fail-open branch's own state, legible without a string match on
        # `status` -- true exactly when the early `if degraded:` return below
        # fires. Additive only: never read by `ok`/`block` themselves.
        "degraded": bool(degraded),
        "hard_block": False,
        "boy_scout_block": False,
        "above_floor": fixable_ceiling > floor_F,
        "messages": [],
    }

    if degraded:
        verdict.update(ok=True, block=False, status="degraded")
        verdict["messages"].append(
            "ADVISORY: dup-ratchet degraded (never blocks): " + "; ".join(degraded)
        )
        return verdict

    hard_block = bool(new_code or new_doc)
    boy_scout_block, boy_scout_status = _boy_scout_arm(
        above_floor=verdict["above_floor"],
        anchor=anchor,
        anchor_is_ancestor=anchor_is_ancestor,
        stagnation=stagnation,
        escalation_K=escalation_K,
    )
    block = hard_block or boy_scout_block
    verdict.update(
        ok=not block, block=block, hard_block=hard_block, boy_scout_block=boy_scout_block
    )

    if hard_block:
        verdict["status"] = "hard-block"
        verdict["messages"].append(
            f"FAIL (hard arm): {len(new_code)} new code + {len(new_doc)} new doc fixable-eligible "
            "family(ies) introduced. Remove the duplication, or classify the family 'intentional' "
            "in dup-review.json, or deliberately accept it into the gate baseline."
        )
    elif boy_scout_block:
        verdict["status"] = "boy-scout-escalation-block"
        verdict["messages"].append(
            f"FAIL (boy-scout escalation): fixable_ceiling={fixable_ceiling} > floor_F={floor_F} and "
            f"{stagnation} commit(s) since the last overlay review (>= escalation_K={escalation_K}). "
            "Lower the ceiling by removing some reviewed fixable duplication (edit dup-review.json to "
            "reset the clock)."
        )
    elif verdict["above_floor"]:
        verdict["status"] = boy_scout_status
        verdict["messages"].append(
            f"ADVISORY (boy-scout): fixable_ceiling={fixable_ceiling} > floor_F={floor_F}; "
            "chip the reviewed fixable duplication down when you touch this area."
        )
    else:
        verdict["status"] = "clean"
        verdict["messages"].append(
            f"OK: no new fixable-eligible families; fixable_ceiling={fixable_ceiling} <= floor_F={floor_F}."
        )
    return verdict
