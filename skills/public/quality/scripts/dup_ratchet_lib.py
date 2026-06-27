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
seams below are separate and injectable) so the policy stays pure and testable.
An anchor that is not an ancestor of HEAD (rebase/squash/force-push orphaned it)
softens the boy-scout arm to advisory ("re-baseline needed"); it never blocks on a
phantom. Overlay/baseline/nose missing => degraded advisory, never a block (FD8).
"""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any, Iterable

GATE_BASELINE_SCHEMA_VERSION = "charness.quality.dup_ratchet_baseline.v2"
GATE_BASELINE_NOTE = (
    "Accepted code clone content fingerprints for the boy-scout dup ratchet (item 5, slice 4). "
    "A code family fingerprint present now but absent here (and not 'intentional' in dup-review.json) "
    "is a NEW fixable-eligible family and hard-blocks. Keyed by a gate-computed, offset/path-"
    "INDEPENDENT content fingerprint (sha256 over the sorted, duplicate-preserving rstrip-normalized "
    "member spans; see nose_fingerprint_lib) from a FULL `nose query` over the scope — NOT nose's "
    "offset/path-folding family_id (slice 4 re-key, resolving deferred decision D30). CHURN CAVEAT: "
    "the fingerprint is STABLE across pure line-shifts (inserting lines above an unchanged span no "
    "longer rotates it), so incidental member-file edits do not force a re-baseline. Re-baseline "
    "deliberately on: a reviewed new/changed family, a member-set (membership) change, a nose-version "
    "bump that regroups families, OR a fingerprint_algo_version bump. The baseline stamps the producing "
    "nose tool_version AND fingerprint_algo_version; the gate WARNS (never degrades) on either skew, so "
    "a silent bump's drift reads as re-baseline, not new dup. Docs key on the doc-nose-baseline signature."
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
def build_gate_baseline(
    code_family_fingerprints: Iterable[str],
    *,
    tool_version: str = "",
    algo_version: str = "",
    note: str = GATE_BASELINE_NOTE,
) -> dict[str, Any]:
    ids = sorted({str(fid) for fid in code_family_fingerprints if fid})
    baseline: dict[str, Any] = {
        "schemaVersion": GATE_BASELINE_SCHEMA_VERSION,
        "note": note,
        "code_family_fingerprints": ids,
    }
    # Stamp only when known so a legacy write stays unstamped, never a false skew.
    if tool_version:
        baseline["tool_version"] = str(tool_version)
    if algo_version:
        baseline["fingerprint_algo_version"] = str(algo_version)
    return baseline


def load_gate_baseline_ids(data: Any) -> set[str] | None:
    """Return the accepted code fingerprint set, or ``None`` when the file is
    absent/unreadable/malformed OR keyed by the legacy ``code_family_ids`` (pre-slice-4
    nose-id baseline) — both read as ``None`` so the CLI degrades to advisory (FD8) until
    a deliberate re-baseline mints the new identity. The function name stays
    identity-agnostic ("the accepted identity set"); only the key it reads changed.
    No dual-read: a stale checkout must NOT misread nose ids as fingerprints."""
    if not isinstance(data, dict):
        return None
    ids = data.get("code_family_fingerprints")
    if not isinstance(ids, list):
        return None
    return {str(fid) for fid in ids if isinstance(fid, str) and fid}


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
    ids = data.get("code_family_fingerprints")
    if not isinstance(ids, list):
        errors.append("code_family_fingerprints must be a list")
        return errors
    for index, value in enumerate(ids):
        if not isinstance(value, str) or not value:
            errors.append(f"code_family_fingerprints[{index}] must be a non-empty string")
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
