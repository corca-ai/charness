#!/usr/bin/env python3
"""Boy-scout duplicate ratchet gate (item 5, slice 2).

Standalone adapter-driven gate: reads the `dup_ratchet` block from the quality
adapter, derives the current code/doc duplicate families, and blocks when a NEW
fixable-eligible family is introduced (hard arm) or when the reviewed fixable
ceiling has stagnated above the healthy floor for too long (boy-scout escalation).
The policy lives in `dup_ratchet_lib` (pure, unit-tested); this CLI is the
integration seam (adapter load, nose query scans, git-derived stagnation).

Portable by construction: a consumer points `review_artifact_path`,
`gate_baseline_path`, and `scope_paths` at its own repo; an absent / disabled
`dup_ratchet` block leaves the gate fully inert (exit 0). charness wires this into
`run-quality.sh` + the broad pre-push path (NOT the docs-only fast subset). See
`references/dup-ratchet.md`.

Test seams: `--code-inventory` / `--doc-inventory` inject pre-collected `--json`
payloads (no nose needed); `--stagnation` injects the commit distance (no git
needed). `--write-baseline` seeds the gate baseline from a full code scan; a
re-baseline that shifts the accepted family_ids by more than
`--baseline-delta-threshold` requires an explicit `--confirm-baseline-delta`
(a deliberate nose-version swing or reviewed batch accept), never a silent overwrite.
It is still a full-scan overwrite though, silently re-accepting every unreviewed new
family too — for routine rotation churn prefer the scoped mode instead:
`--accept-rotation OLD_ID=NEW_ID` / `--accept-family NEW_ID` (both repeatable) apply
ONLY the named pairs/ids onto the existing baseline and refuse any other live delta
(listing it); `--write-baseline` prints a WARN naming this path on overwrite.

Advisory (degraded, never blocks) inputs: overlay/baseline/nose missing, an empty
`scope_paths` while enabled (falls back to nose DEFAULT_PATHS), and a present but
schema-invalid gate baseline (validated via `dup_ratchet_baseline_lib.validate_gate_baseline`).

Exit 0 when clean, inert, or degraded. Exit 1 on a real block, an invalid adapter
(fails closed), or a refused unconfirmed large `--write-baseline` overwrite.

Reduction pre-pass (schema v3, item 5 slice D, S4-Defer-3): before `evaluate` runs, a
candidate-new fingerprint whose member-hash multiset is a PROPER sub-multiset of a
vanished baseline family's is classified a membership REDUCTION (a copy of a clone
was removed) rather than new duplication. Reduced fingerprints are excluded from the
set `evaluate` is asked about — `evaluate`'s own pure set-diff signature (S4-D9) is
untouched — and the CLI always prints one advisory line per reduction (never silent),
naming the one-shot `--accept-rotation OLD=NEW` that folds it into the baseline.
"""

from __future__ import annotations

import argparse
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
_ratchet_git = SKILL_RUNTIME.load_local_skill_module(__file__, "dup_ratchet_git")
_scan = SKILL_RUNTIME.load_local_skill_module(__file__, "dup_ratchet_scan")
_nose_report = SKILL_RUNTIME.load_local_skill_module(__file__, "nose_report_lib")
_fingerprint = SKILL_RUNTIME.load_local_skill_module(__file__, "nose_fingerprint_lib")
_quality_adapter = SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.quality_adapter_lib")

DEFAULT_REVIEW_REL = "charness-artifacts/quality/dup-review.json"
DEFAULT_GATE_BASELINE_REL = "charness-artifacts/quality/dup-ratchet-baseline.json"
# C: --write-baseline guardrail. A re-baseline whose added+removed family_id count
# exceeds this requires an explicit --confirm-baseline-delta (a deliberate nose
# scanner-version swing or a reviewed batch accept is the legitimate large case).
# Consumers can tune it via --baseline-delta-threshold. Never affects the gate
# evaluate path — only the maintenance --write-baseline command.
DEFAULT_BASELINE_DELTA_THRESHOLD = 50


def _resolve_stagnation(repo_root: Path, review_rel: str, args) -> tuple[int | None, str | None, bool]:
    if args.stagnation is not None:
        return args.stagnation, "<injected>", True
    anchor = _ratchet_git.resolve_anchor(repo_root, review_rel)
    is_ancestor = _ratchet_git.anchor_is_ancestor(repo_root, anchor)
    stagnation = _ratchet_git.stagnation_commits(repo_root, anchor) if is_ancestor else None
    return stagnation, anchor, is_ancestor


def _write_gate_baseline(out: Path, members: dict, live_version: str) -> None:
    baseline = _ratchet_baseline.build_gate_baseline(
        members, tool_version=live_version, algo_version=_fingerprint.FINGERPRINT_ALGO_VERSION
    )
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(baseline, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_baseline(repo_root: Path, config: dict, args) -> dict:
    scope_paths = list(config.get("scope_paths") or [])
    baseline_rel = config.get("gate_baseline_path") or DEFAULT_GATE_BASELINE_REL
    members, reason, live_version = _scan.code_family_members(args, repo_root, scope_paths)
    if reason:
        return {"ok": False, "inert": False, "status": "write-baseline-failed",
                "messages": [f"cannot write gate baseline: {reason}"]}
    ids = set(members)
    out = repo_root / baseline_rel
    # C: guard a large, possibly-accidental rewrite of the accepted baseline. A
    # deliberate re-baseline (a nose scanner-version swing re-hashes every family_id;
    # a reviewed batch accept) is the legitimate large-delta case — it proceeds with
    # --confirm-baseline-delta. This is the maintenance command refusing a silent
    # overwrite; it never touches the gate evaluate path, so it cannot false-block a push.
    existing_ids = _ratchet_baseline.load_gate_baseline_ids(_scan.load_json(out))
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
    _write_gate_baseline(out, members, live_version)
    message = f"wrote gate baseline ({len(ids)} code family fingerprints) -> {baseline_rel}"
    if delta_note:
        message += f" [{delta_note}]"
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


def _scoped_rebaseline(repo_root: Path, config: dict, args) -> dict:
    """Scoped re-baseline (see module docstring): apply ONLY named rotations /
    new-family accepts onto the existing baseline; refuse any other live delta."""
    scope_paths = list(config.get("scope_paths") or [])
    baseline_rel = config.get("gate_baseline_path") or DEFAULT_GATE_BASELINE_REL
    out = repo_root / baseline_rel
    existing_members = _ratchet_baseline.load_gate_baseline_members(_scan.load_json(out))
    if existing_members is None:
        return {"ok": False, "inert": False, "status": "scoped-rebaseline-failed",
                "messages": [f"no readable gate baseline at {baseline_rel}; run --write-baseline "
                             "once to seed one before using scoped accepts."]}
    existing_ids = set(existing_members)
    live_members, reason, live_version = _scan.code_family_members(args, repo_root, scope_paths)
    if reason:
        return {"ok": False, "inert": False, "status": "scoped-rebaseline-failed",
                "messages": [f"cannot compute live fingerprints: {reason}"]}
    live_ids = set(live_members)
    accept_families = list(args.accept_family or [])
    rotations, malformed = _ratchet.parse_rotations(args.accept_rotation or [])
    plan = _ratchet.plan_scoped_rebaseline(
        existing_ids=existing_ids, live_ids=live_ids, rotations=rotations, accept_families=accept_families,
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
    _write_gate_baseline(out, updated_members, live_version)
    message = (
        f"scoped re-baseline: accepted {len(rotations)} rotation(s) + {len(accept_families)} new "
        f"family(ies); baseline now has {len(updated_ids)} code family fingerprints -> {baseline_rel}"
    )
    return {"ok": True, "inert": False, "status": "scoped-rebaseline-written",
            "accepted_rotations": [{"old": old, "new": new} for old, new in rotations],
            "accepted_families": accept_families, "code_family_count": len(updated_ids),
            "gate_baseline_path": baseline_rel, "tool_version": live_version, "messages": [message]}


def _evaluate_config(repo_root: Path, config: dict, args) -> dict:
    floor_F = int(config.get("floor_F", 0))
    # The validated adapter always supplies these; the fallbacks match the policy
    # defaults (DEFAULT_DUP_RATCHET) so an ad-hoc/unvalidated config can't silently
    # escalate at K=1 instead of the documented 10.
    escalation_K = int(config.get("escalation_K", 10))
    scope_paths = list(config.get("scope_paths") or [])
    review_rel = config.get("review_artifact_path") or DEFAULT_REVIEW_REL
    baseline_rel = config.get("gate_baseline_path") or DEFAULT_GATE_BASELINE_REL

    degraded: list[str] = []
    if not scope_paths:
        # F: enabled but no scope_paths. A real code scan then falls back to nose
        # DEFAULT_PATHS (likely the wrong tree on a consumer repo). Advisory only
        # (FD8 whole-gate degrade) — never blocks, never reads as a silent clean pass.
        degraded.append(
            "dup_ratchet.enabled is true but scope_paths is empty; a real code scan "
            "falls back to nose DEFAULT_PATHS (likely the wrong tree). Set scope_paths "
            "to this repo's code roots."
        )
    overlay = _scan.load_json(repo_root / review_rel)
    if overlay is None:
        degraded.append(f"overlay missing/unreadable ({review_rel})")
    raw_baseline = _scan.load_json(repo_root / baseline_rel)
    baseline_ids = _ratchet_baseline.load_gate_baseline_ids(raw_baseline)
    baseline_members = _ratchet_baseline.load_gate_baseline_members(raw_baseline)
    baseline_version = _ratchet_baseline.load_gate_baseline_tool_version(raw_baseline)
    baseline_algo = _ratchet_baseline.load_gate_baseline_algo_version(raw_baseline)
    if baseline_ids is None:
        degraded.append(f"gate baseline missing/unreadable ({baseline_rel})")
    elif (integrity := _ratchet_baseline.validate_gate_baseline(raw_baseline)):
        # I: a present, loadable baseline can still be schema-invalid (wrong
        # schemaVersion, non-string ids). validate_gate_baseline was defined+tested
        # but wired to nothing; fold it in here so a silent integrity drift surfaces
        # as advisory through the existing dup-ratchet phase. Advisory only (FD8).
        degraded.append(f"gate baseline integrity ({baseline_rel}): " + "; ".join(integrity))
    live_members, code_reason, live_version = _scan.code_family_members(args, repo_root, scope_paths)
    code_ids = set(live_members)
    if code_reason:
        degraded.append(code_reason)
    elif args.code_inventory is None and not code_ids and baseline_ids:
        # A real scan that yields zero families against a non-empty gate baseline is
        # almost certainly a broken scan or misconfigured scope_paths, not a repo that
        # lost all its clone families. Treat it as degraded so it cannot read as a
        # silent clean pass (an empty injected inventory is a deliberate test, not this).
        degraded.append(
            f"code scan returned 0 families but the gate baseline has {len(baseline_ids)}; "
            "likely a broken scan or misconfigured scope_paths"
        )
    doc_signatures, doc_reason = _scan.doc_drift_signatures(args, repo_root)
    if doc_reason:
        degraded.append(doc_reason)

    intentional_code, intentional_doc = _ratchet.overlay_intentional(overlay)
    # Reduction pre-pass (S4-Defer-3): classify each would-be-new fingerprint that is
    # actually a membership-shrunk remainder of a vanished baseline family, so it never
    # reaches evaluate()'s hard-block set. evaluate()'s own signature stays untouched
    # (S4-D9); this only trims the id set handed to it.
    candidate_new = code_ids - (baseline_ids or set()) - intentional_code
    reductions = _ratchet.classify_reductions(live_members, baseline_members or {}, candidate_new)
    code_ids_for_evaluate = code_ids - {r["new_fingerprint"] for r in reductions}
    stagnation, anchor, is_ancestor = _resolve_stagnation(repo_root, review_rel, args)
    verdict = _ratchet.evaluate(
        code_family_ids=code_ids_for_evaluate, gate_baseline_ids=baseline_ids or set(),
        doc_drift_signatures=doc_signatures, intentional_code_ids=intentional_code,
        intentional_doc_signatures=intentional_doc,
        fixable_ceiling=_ratchet.overlay_fixable_ceiling(overlay),
        floor_F=floor_F, escalation_K=escalation_K, stagnation=stagnation,
        anchor=anchor, anchor_is_ancestor=is_ancestor, degraded_reasons=degraded,
    )
    verdict["inert"] = False
    # A reduction is NEVER silent, even on an otherwise-clean run: print one advisory
    # line per reduction naming the scoped-accept hint that folds it into the baseline.
    verdict["reductions"] = reductions
    for reduction in reductions:
        verdict["messages"].append(
            f"ADVISORY (reduction): family {reduction['old_fingerprint']} shrank to "
            f"{reduction['new_fingerprint']} (membership reduction, not new duplication); "
            f"accept with --accept-rotation {reduction['old_fingerprint']}={reduction['new_fingerprint']}"
        )
    # Scanner-version skew is a WARNING, never a degrade: surface it ON the verdict
    # (a block stays a block) so the operator reads a wall of "new" families as
    # version-rotation to re-baseline, not real duplication to remove. degrading here
    # would silently drop the gate and let genuine new dup through.
    skew = _nose_report.tool_version_skew(baseline_version, live_version)
    verdict["version_skew"] = skew
    if skew:
        verdict["messages"].append(f"WARNING (scanner-version skew): {skew}")
    # Independent of the nose-version axis above: the gate-owned fingerprint algo version.
    # Either skew is a re-baseline signal; each names its axis so recovery is unambiguous.
    # Neither degrades — a block stays a block (suppressing would hide real new dup).
    algo_skew = _ratchet_baseline.algo_version_skew(baseline_algo, _fingerprint.FINGERPRINT_ALGO_VERSION)
    verdict["algo_skew"] = algo_skew
    if algo_skew:
        verdict["messages"].append(f"WARNING (fingerprint-algo skew): {algo_skew}")
    return verdict


def run(repo_root: Path, args) -> dict:
    adapter = _quality_adapter.load_quality_adapter_strict(repo_root)
    if adapter.get("errors"):
        return {"ok": False, "inert": False, "status": "adapter-invalid",
                "adapter_errors": list(adapter["errors"]),
                "messages": ["quality adapter invalid: " + "; ".join(str(e) for e in adapter["errors"])]}
    config = adapter["data"].get("dup_ratchet") or {}
    if args.accept_rotation or args.accept_family:
        return _scoped_rebaseline(repo_root, config, args)
    if args.write_baseline:
        return _write_baseline(repo_root, config, args)
    if not config.get("enabled"):
        return {"ok": True, "inert": True, "status": "inert",
                "messages": ["dup_ratchet.enabled is false; gate inert (opted out)."]}
    return _evaluate_config(repo_root, config, args)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Boy-scout duplicate ratchet gate.")
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--code-inventory", type=Path, help="Injected full-scan inventory_nose_clones --json file; else a full nose query scan runs.")
    parser.add_argument("--doc-inventory", type=Path, help="Injected inventory_doc_duplicates --json drift file; else the doc inventory runs.")
    parser.add_argument("--stagnation", type=int, default=None, help="Inject the stagnation commit distance (test seam); else derived from git.")
    parser.add_argument("--write-baseline", action="store_true", help="Seed the gate baseline from a full code scan and exit (accept today's code family_ids).")
    parser.add_argument("--confirm-baseline-delta", action="store_true", help="Confirm a deliberate large re-baseline (--write-baseline) past the delta threshold, e.g. a nose scanner-version swing.")
    parser.add_argument("--baseline-delta-threshold", type=int, default=DEFAULT_BASELINE_DELTA_THRESHOLD, help="Large-delta guardrail for --write-baseline: added+removed family_ids over this requires --confirm-baseline-delta.")
    parser.add_argument("--accept-rotation", action="append", metavar="OLD_ID=NEW_ID", help="Scoped re-baseline: rotate one accepted fingerprint (repeatable). Refuses any other live delta not named here or via --accept-family.")
    parser.add_argument("--accept-family", action="append", metavar="NEW_ID", help="Scoped re-baseline: accept one new fingerprint into the baseline (repeatable). Combine with --accept-rotation; any unnamed live delta is refused.")
    parser.add_argument("--json", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    repo_root = args.repo_root.resolve()
    report = run(repo_root, args)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        for message in report.get("messages", []):
            print(message)
    return 0 if report.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
