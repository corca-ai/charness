#!/usr/bin/env python3
"""Boy-scout duplicate ratchet — pure policy + gate-baseline + git seams (item 5, slice 2).

Slice 1 built the reviewed-fixable overlay (``dup_review_lib`` / ``dup-review.json``).
This module is the ratchet's teeth: given the current duplicate families, the
accepted baselines, and the overlay classifications, it decides whether a push
should block. It is the portable unit (a standalone gate script + payload
contract, mirroring ``references/boundary-bypass-ratchet.md``); ``check_dup_ratchet.py``
is one consumer (charness wires it into ``run-quality.sh`` + broad pre-push).

Two arms (spec Fixed Decision 1 + Slice 2 D1–D3):

- **Hard arm (always):** a NEW fixable-eligible family hard-blocks. "New" =
  present now, absent from the accepted reference, not classified ``intentional``.
  Code newness diffs the current ``family_id`` set against a gate-owned
  ``family_id`` baseline (``dup-ratchet-baseline.json``), NOT nose's ``key``-based
  ``--baseline`` — for plumbing reasons: ``query`` takes one root per call and
  ``--write-baseline`` clobbers its target each run, so a multi-root scope cannot
  share one native baseline. CHURN CAVEAT: the gate keys on ``family_id`` for that
  plumbing reason, NOT because it is churn-stable — it is NOT. The family ``id``
  folds every member's per-span id, and each per-span id folds the span's normalized
  content, its **line offset**, AND its **file path**. So editing any scanned member
  file — even inserting lines *above* an unchanged duplicated span — shifts that
  member's offset, rotates its id, and rotates the whole family ``id``, even for the
  byte-identical sibling copies in unrelated files (the same "an unchanged copy
  re-keys when a sibling changes" failure nose's ``key`` has). A rotated id reads as
  a brand-new family (hard arm blocks) with ZERO new duplication; the honest recovery
  is a deliberate ``--write-baseline`` re-baseline — verify the rotated families are
  byte-identical base-vs-HEAD first, then treat re-baseline-on-member-edit as expected
  maintenance, the same discipline as a scanner-version bump. Doc newness instead
  reuses the position-independent ``signature`` drift (``doc-nose-baseline.json``,
  ``path#heading`` — stable across line-number churn). Recording a new family
  ``unreviewed`` does NOT unblock it (D3).
- **Boy-scout arm (escalating nudge):** while ``fixable_ceiling > floor_F`` and the
  reviewed overlay has not advanced (``stagnation_commits >= escalation_K``), the
  normally-advisory "remove existing fixable dup" nudge escalates to a one-time
  block, which resets when the overlay edit advances the git anchor. At/below the
  healthy floor ``F`` the boy-scout arm is fully advisory; the hard arm still fires.

Stagnation is measured from git, not a stored counter or self-SHA (FD5): the anchor
is the commit that last touched the overlay; stagnation = ``rev-list --count
<anchor>..HEAD``. ``evaluate`` takes the stagnation distance *injected* (the git
seams below are separate and injectable) so the policy stays pure and testable.
An anchor that is not an ancestor of HEAD (rebase/squash/force-push orphaned it)
softens the boy-scout arm to advisory ("re-baseline needed"); it never blocks on a
phantom. Overlay/baseline/nose missing => degraded advisory, never a block (FD8).
"""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any, Iterable

GATE_BASELINE_SCHEMA_VERSION = "charness.quality.dup_ratchet_baseline.v1"
GATE_BASELINE_NOTE = (
    "Accepted code clone family_ids for the boy-scout dup ratchet (item 5, slice 2). "
    "A code family_id present now but absent here (and not 'intentional' in dup-review.json) "
    "is a NEW fixable-eligible family and hard-blocks. Keyed by nose family_id (16-hex "
    "content hash) from a FULL `nose query` (one call per scope root, deduped) — NOT nose's "
    "`key`/--baseline (one root per query, clobbers each run). CHURN CAVEAT: family_id is NOT "
    "churn-stable — it folds member span offset + file path, so editing any scanned member "
    "file (even adding lines above an unchanged span) rotates it and forces a re-baseline with "
    "zero new duplication. Docs key on the position-independent doc-nose-baseline signature "
    "instead, not here. Re-baseline deliberately (to accept reviewed new families) per scanner "
    "version AND on member-file edits that rotate ids (verify byte-identical base-vs-HEAD)."
)


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
# Gate baseline (dup-ratchet-baseline.json) load/build/validate
# --------------------------------------------------------------------------- #
def build_gate_baseline(code_family_ids: Iterable[str], *, note: str = GATE_BASELINE_NOTE) -> dict[str, Any]:
    ids = sorted({str(fid) for fid in code_family_ids if fid})
    return {"schemaVersion": GATE_BASELINE_SCHEMA_VERSION, "note": note, "code_family_ids": ids}


def load_gate_baseline_ids(data: Any) -> set[str] | None:
    """Return the accepted code family_id set, or ``None`` when the file is
    absent/unreadable/malformed (the CLI treats ``None`` as degraded => advisory)."""
    if not isinstance(data, dict):
        return None
    ids = data.get("code_family_ids")
    if not isinstance(ids, list):
        return None
    return {str(fid) for fid in ids if isinstance(fid, str) and fid}


def validate_gate_baseline(data: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["gate baseline must be a JSON object"]
    if data.get("schemaVersion") != GATE_BASELINE_SCHEMA_VERSION:
        errors.append(f"schemaVersion must be {GATE_BASELINE_SCHEMA_VERSION!r}")
    ids = data.get("code_family_ids")
    if not isinstance(ids, list):
        errors.append("code_family_ids must be a list")
        return errors
    for index, value in enumerate(ids):
        if not isinstance(value, str) or not value:
            errors.append(f"code_family_ids[{index}] must be a non-empty string")
    return errors


# --------------------------------------------------------------------------- #
# Git seams (injectable per FD5; evaluate takes the distance, never inlines git)
# --------------------------------------------------------------------------- #
def _git_output(repo_root: Path, args: list[str]) -> tuple[int, str]:
    try:
        result = subprocess.run(["git", *args], cwd=repo_root, capture_output=True, text=True)
    except OSError:
        return 1, ""
    return result.returncode, result.stdout.strip()


def resolve_anchor(repo_root: Path, review_artifact_rel: str, head: str = "HEAD") -> str | None:
    """The commit that last touched the overlay (``git log -1 --format=%H``). The
    anchor advancing (an overlay edit, e.g. lowering the ceiling) resets stagnation."""
    rc, out = _git_output(repo_root, ["log", "-1", "--format=%H", head, "--", review_artifact_rel])
    if rc != 0 or not out:
        return None
    return out.splitlines()[0].strip() or None


def anchor_is_ancestor(repo_root: Path, anchor: str | None, head: str = "HEAD") -> bool:
    if not anchor:
        return False
    rc, _ = _git_output(repo_root, ["merge-base", "--is-ancestor", anchor, head])
    return rc == 0


def stagnation_commits(repo_root: Path, anchor: str | None, head: str = "HEAD") -> int | None:
    """Commits over ``<anchor>..<head>`` (FD5). ``None`` when the anchor is unknown
    or git cannot answer — the caller degrades the boy-scout arm to advisory."""
    if not anchor:
        return None
    rc, out = _git_output(repo_root, ["rev-list", "--count", f"{anchor}..{head}"])
    if rc != 0:
        return None
    try:
        return int(out.strip())
    except ValueError:
        return None


# --------------------------------------------------------------------------- #
# Policy
# --------------------------------------------------------------------------- #
def _boy_scout_arm(
    *, above_floor: bool, anchor: str | None, anchor_is_ancestor: bool,
    stagnation: int | None, escalation_K: int,
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
        above_floor=verdict["above_floor"], anchor=anchor,
        anchor_is_ancestor=anchor_is_ancestor, stagnation=stagnation, escalation_K=escalation_K,
    )
    block = hard_block or boy_scout_block
    verdict.update(ok=not block, block=block, hard_block=hard_block, boy_scout_block=boy_scout_block)

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
