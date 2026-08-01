"""The three ways this gate writes its accepted baseline, and what each refuses.

Split out of `check_dup_ratchet` because "mutate the baseline" is one concern with
one invariant -- never absorb an unreviewed family -- expressed three ways:

- `write_baseline`: full-scan overwrite. Absorbs everything, so it guards a large
  delta behind an explicit confirmation and warns on any overwrite.
- `scoped_rebaseline`: applies ONLY named rotations/accepts, refusing anything else.
- `restamp_tool_version`: rewrites the scanner stamp only, refusing any set change.

The gate's evaluate path is deliberately not here: none of these can reach it, so
none of them can false-block a push.
"""

from __future__ import annotations

import json
import runpy
from pathlib import Path
from types import SimpleNamespace


def _load_skill_runtime_bootstrap():
    bootstrap = next((ancestor / "skill_runtime_bootstrap.py" for ancestor in Path(__file__).resolve().parents if (ancestor / "skill_runtime_bootstrap.py").is_file()), None)
    if bootstrap is None:
        raise ImportError("skill_runtime_bootstrap.py not found")
    return SimpleNamespace(**runpy.run_path(str(bootstrap)))


SKILL_RUNTIME = _load_skill_runtime_bootstrap()
_ratchet = SKILL_RUNTIME.load_local_skill_module(__file__, "dup_ratchet_lib")
_ratchet_baseline = SKILL_RUNTIME.load_local_skill_module(__file__, "dup_ratchet_baseline_lib")
_scan = SKILL_RUNTIME.load_local_skill_module(__file__, "dup_ratchet_scan")
_fingerprint = SKILL_RUNTIME.load_local_skill_module(__file__, "nose_fingerprint_lib")

DEFAULT_REVIEW_REL = "charness-artifacts/quality/dup-review.json"
DEFAULT_GATE_BASELINE_REL = "charness-artifacts/quality/dup-ratchet-baseline.json"


def write_gate_baseline(out: Path, members: dict, live_version: str) -> None:
    baseline = _ratchet_baseline.build_gate_baseline(
        members, tool_version=live_version, algo_version=_fingerprint.FINGERPRINT_ALGO_VERSION
    )
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(baseline, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_baseline(repo_root: Path, config: dict, args) -> dict:
    baseline_rel, members, live_version, error = _scan.live_scan_for_rebaseline(
        repo_root, config, args, default_baseline_rel=DEFAULT_GATE_BASELINE_REL,
        fail_status="write-baseline-failed", fail_prefix="cannot write gate baseline",
    )
    if error:
        return error
    ids = set(members)
    out = repo_root / baseline_rel
    # A zero-family scan writes an EMPTY accepted baseline and reports success, which then
    # disarms the gate's own "0 families but the baseline has N" backstop (that check is
    # keyed on a non-empty baseline). nose exits 0 with `families: []` over a scope root
    # that matches no supported files (probed 2026-07-28), so a renamed or mistyped
    # `dup_ratchet.scope_paths` reaches here — and on FIRST-TIME bootstrap the large-delta
    # guard below is skipped entirely, so nothing else stops it. A genuinely clone-free
    # scope is real, so this is a confirmation gate rather than a hard refusal.
    if not ids and not args.confirm_baseline_delta:
        return {
            "ok": False, "inert": False, "status": "empty-scan-unconfirmed",
            "code_family_count": 0, "gate_baseline_path": baseline_rel,
            "messages": [
                "refusing to write an EMPTY gate baseline: the live scan established zero clone "
                "families, which is usually a broken scan or a misconfigured dup_ratchet.scope_paths "
                "rather than a clone-free repo. An empty accepted baseline also disarms the gate's "
                "zero-family backstop. If the scope really is clone-free, re-run with "
                "--confirm-baseline-delta.",
            ],
        }
    # C: guard a large, possibly-accidental rewrite of the accepted baseline. A
    # deliberate re-baseline (a nose scanner-version swing re-hashes every family_id;
    # a reviewed batch accept) is the legitimate large-delta case — it proceeds with
    # --confirm-baseline-delta. This is the maintenance command refusing a silent
    # overwrite; it never touches the gate evaluate path, so it cannot false-block a push.
    existing_ids = _ratchet_baseline.load_gate_baseline_ids(_scan.load_json(out))
    # An unreadable baseline and an absent one both arrive here as None, and the delta
    # guard below is keyed on `existing_ids is not None` — so a truncated, malformed, or
    # legacy-shaped baseline used to take the first-time-bootstrap path and get silently
    # overwritten, no matter how large the delta (sweep row S28). The file's existence is
    # the fact that separates the two, and the sibling `scoped_rebaseline` below already
    # refuses this same state; this is that refusal, made consistent. A deliberate rewrite
    # of a legacy or damaged baseline is legitimate, so it is a confirmation gate rather
    # than a hard refusal.
    existing_unreadable = existing_ids is None and out.is_file()
    if existing_unreadable and not args.confirm_baseline_delta:
        return {
            "ok": False, "inert": False, "status": "existing-baseline-unreadable",
            "code_family_count": len(ids), "gate_baseline_path": baseline_rel,
            "messages": [
                f"refusing to overwrite {baseline_rel}: the file exists but no accepted family set "
                "could be read from it (truncated, malformed, or a legacy shape). Overwriting it "
                "would discard a reviewed baseline through the first-time-bootstrap path, which "
                "skips the large-delta guard entirely. Inspect the file, then re-run with "
                "--confirm-baseline-delta if the rewrite is deliberate.",
            ],
        }
    delta_note = None
    if existing_ids is not None:
        added, removed = ids - existing_ids, existing_ids - ids
        delta = len(added) + len(removed)
        if delta > args.baseline_delta_threshold:
            if not args.confirm_baseline_delta:
                return {
                    "ok": False, "inert": False, "status": "baseline-delta-unconfirmed",
                    "baseline_delta": {"added": len(added), "removed": len(removed),
                                       "threshold": args.baseline_delta_threshold},
                    "messages": [
                        f"refusing to overwrite the gate baseline: delta {delta} "
                        f"(+{len(added)}/-{len(removed)}) exceeds the large-delta threshold "
                        f"({args.baseline_delta_threshold}). If this is a deliberate "
                        "re-baseline (e.g. a nose scanner-version change, or a reviewed "
                        "batch accept), re-run with --confirm-baseline-delta; otherwise it "
                        "is likely a broken scan or misconfigured scope_paths.",
                    ],
                }
            delta_note = f"confirmed large delta (+{len(added)}/-{len(removed)})"
    # Stamp the producing nose version from THIS scan (the run that minted these
    # fingerprints) plus the fingerprint algo version, never a fresh probe — so the stamps
    # can never disagree with the fingerprints they label.
    write_gate_baseline(out, members, live_version)
    message = f"wrote gate baseline ({len(ids)} code family fingerprints) -> {baseline_rel}"
    if delta_note:
        message += f" [{delta_note}]"
    if existing_unreadable:
        # One flag now attests three different facts (empty scan, unreadable existing
        # baseline, large delta). Recording WHICH one it covered keeps a confirmation of
        # a reviewed large delta from silently also covering the discard of a damaged
        # baseline the operator never inspected.
        message += (
            f" [--confirm-baseline-delta also discarded an UNREADABLE existing baseline at "
            f"{baseline_rel}; its previous accepted set was not recoverable and is gone]"
        )
    messages = [message]
    if existing_ids is not None:  # overwrite, not first-time bootstrap
        messages.append(
            "WARN: --write-baseline is a full-scan overwrite that silently re-accepts every "
            "current family, including unreviewed new ones. Prefer --accept-rotation "
            "OLD_ID=NEW_ID / --accept-family NEW_ID for routine re-baseline churn; reserve "
            "--write-baseline for first-time bootstrap or a deliberate, reviewed full re-baseline."
        )
    return {"ok": True, "inert": False, "status": "baseline-written",
            "code_family_count": len(ids), "gate_baseline_path": baseline_rel,
            "tool_version": live_version, "messages": messages}


def restamp_tool_version(repo_root: Path, config: dict, args) -> dict:
    """Re-stamp the baseline's scanner version WITHOUT touching the family set.

    A nose bump re-stamps nothing on its own, so the skew warning persists on every
    run until someone re-baselines. But the only paths that re-stamp were
    `--write-baseline` (absorbs every unreviewed new family) and the scoped accepts
    (require naming an id), so the honest fix for "the version moved and nothing
    else did" did not exist and the warning became furniture.

    This path exists only for that case and proves it before writing: if the live
    fixable-eligible family SET differs from the baseline's in either direction, the
    bump regrouped families, the stored set is genuinely stale, and a re-stamp would
    assert a review that never happened. So it refuses and names the delta.
    """
    baseline_rel, live_members, live_version, error = _scan.live_scan_for_rebaseline(
        repo_root, config, args, default_baseline_rel=DEFAULT_GATE_BASELINE_REL,
        fail_status="restamp-failed", fail_prefix="cannot compute live fingerprints",
    )
    if error:
        return error
    out = repo_root / baseline_rel
    raw_baseline = _scan.load_json(out)
    existing_members = _ratchet_baseline.load_gate_baseline_members(raw_baseline)
    if existing_members is None:
        remedy = (
            "run --write-baseline once to seed one before re-stamping."
            if not out.is_file() else
            "the file EXISTS but no accepted set could be read from it, so --write-baseline "
            "will refuse it too; inspect it, then re-run --write-baseline "
            "--confirm-baseline-delta if the rewrite is deliberate."
        )
        return {"ok": False, "inert": False, "status": "restamp-failed",
                "messages": [f"no readable gate baseline at {baseline_rel}; {remedy}"]}
    baseline_version = _ratchet_baseline.load_gate_baseline_tool_version(raw_baseline)
    added = sorted(set(live_members) - set(existing_members))
    removed = sorted(set(existing_members) - set(live_members))
    if added or removed:
        return {
            "ok": False, "inert": False, "status": "restamp-refused",
            "added": added, "removed": removed,
            "baseline_tool_version": baseline_version, "tool_version": live_version,
            "messages": [
                "refusing to re-stamp: the family SET changed, so this is not a version-only "
                f"skew ({len(added)} added, {len(removed)} removed). A re-stamp would claim the "
                "stored set was reviewed under the new scanner when it was not. Use "
                "--accept-rotation/--accept-family for a named delta, or --write-baseline for a "
                "full reviewed re-baseline.",
            ],
        }
    if baseline_version == live_version:
        return {"ok": True, "inert": False, "status": "restamp-noop",
                "baseline_tool_version": baseline_version, "tool_version": live_version,
                "code_family_count": len(existing_members), "gate_baseline_path": baseline_rel,
                "messages": [f"baseline already stamped {live_version!r}; nothing to re-stamp."]}
    write_gate_baseline(out, existing_members, live_version)
    return {
        "ok": True, "inert": False, "status": "restamp-written",
        "baseline_tool_version": baseline_version, "tool_version": live_version,
        "code_family_count": len(existing_members), "gate_baseline_path": baseline_rel,
        "messages": [
            f"re-stamped scanner version {baseline_version!r} -> {live_version!r} with the family "
            f"set unchanged ({len(existing_members)} code family fingerprints) -> {baseline_rel}",
        ],
    }


def scoped_rebaseline(repo_root: Path, config: dict, args) -> dict:
    """Scoped re-baseline (see module docstring): apply ONLY named rotations /
    new-family accepts onto the existing baseline; refuse any other live delta."""
    baseline_rel, live_members, live_version, error = _scan.live_scan_for_rebaseline(
        repo_root, config, args, default_baseline_rel=DEFAULT_GATE_BASELINE_REL,
        fail_status="scoped-rebaseline-failed", fail_prefix="cannot compute live fingerprints",
    )
    if error:
        return error
    out = repo_root / baseline_rel
    existing_members = _ratchet_baseline.load_gate_baseline_members(_scan.load_json(out))
    if existing_members is None:
        remedy = (
            "run --write-baseline once to seed one before using scoped accepts."
            if not out.is_file() else
            "the file EXISTS but no accepted set could be read from it, so --write-baseline "
            "will refuse it too; inspect it, then re-run --write-baseline "
            "--confirm-baseline-delta if the rewrite is deliberate."
        )
        return {"ok": False, "inert": False, "status": "scoped-rebaseline-failed",
                "messages": [f"no readable gate baseline at {baseline_rel}; {remedy}"]}
    existing_ids = set(existing_members)
    live_ids = set(live_members)
    accept_families = list(args.accept_family or [])
    rotations, malformed = _ratchet.parse_rotations(args.accept_rotation or [])
    # Evaluate-parity universe trim: exempt overlay-intentional families and
    # membership reductions from refusal (they are never absorbed either), so the
    # rotations the evaluate path suggests are acceptable as-is.
    review_rel = config.get("review_artifact_path") or DEFAULT_REVIEW_REL
    exemptions = _ratchet.scoped_rebaseline_exemptions(
        live_members=live_members, existing_members=existing_members,
        overlay=_scan.load_json(repo_root / review_rel),
        named_new_ids={new for _old, new in rotations} | set(accept_families),
    )
    plan = _ratchet.plan_scoped_rebaseline(
        existing_ids=existing_ids, live_ids=live_ids, rotations=rotations, accept_families=accept_families,
        exempt_live_ids=exemptions["exempt_live_ids"],
    )
    errors = [f"malformed --accept-rotation {raw!r}; expected OLD_ID=NEW_ID" for raw in malformed] + plan["errors"]
    if errors:
        return {"ok": False, "inert": False, "status": "scoped-rebaseline-invalid", "messages": errors}
    if plan["refused_added"]:
        return {
            "ok": False, "inert": False, "status": "scoped-rebaseline-refused",
            "refused_added": plan["refused_added"],
            "messages": [
                "refusing to silently accept unnamed new fixable-eligible family(ies) into the baseline "
                f"({', '.join(plan['refused_added'])}). Name each with --accept-rotation OLD_ID=NEW_ID "
                "or --accept-family NEW_ID, or use --write-baseline for a full reviewed re-baseline.",
            ],
        }
    updated_ids = plan["updated_ids"]
    # Each kept/rotated/accepted id's member hashes come from wherever it is still
    # known: unchanged ids from the existing baseline, rotated/accepted ids from the
    # live scan (the only place a brand-new fingerprint's members can come from).
    updated_members = {fid: existing_members.get(fid, live_members.get(fid, [])) for fid in updated_ids}
    write_gate_baseline(out, updated_members, live_version)
    message = (
        f"scoped re-baseline: accepted {len(rotations)} rotation(s) + {len(accept_families)} new "
        f"family(ies); baseline now has {len(updated_ids)} code family fingerprints -> {baseline_rel}"
    )
    return {"ok": True, "inert": False, "status": "scoped-rebaseline-written",
            "accepted_rotations": [{"old": old, "new": new} for old, new in rotations],
            "accepted_families": accept_families, "code_family_count": len(updated_ids),
            "ignored_intentional": exemptions["ignored_intentional"],
            "unnamed_reductions": exemptions["unnamed_reductions"],
            "gate_baseline_path": baseline_rel, "tool_version": live_version,
            "messages": [message, *exemptions["advisories"]]}
