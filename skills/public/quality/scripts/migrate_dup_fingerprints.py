#!/usr/bin/env python3
"""One-shot fingerprint-algorithm migration tool (item 5, slice D).

Reusable across every future ``nose_fingerprint_lib.FINGERPRINT_ALGO_VERSION`` bump
(the v1 -> v2 token-aware-normalization landing is only the first instance of this
migration class): given the CURRENT accepted baselines/overlay (minted under the OLD
algo) and a fresh live nose scan (computing BOTH the old and new algo's identity per
family), remap every accepted identity old -> new across three surfaces:

- ``dup-ratchet-baseline.json`` (gate, schema v3): a SURVIVOR (old v1 fingerprint
  found in the live scan) is remapped to its live v2 fingerprint + member hashes. A
  VANISHED baseline fingerprint (absent from the live scan) is DROPPED with a logged
  note. A live family whose v1 fingerprint was NOT in the old baseline is a
  ``requires_review`` candidate: NOT written unless named via repeatable
  ``--accept-new-family V2_FINGERPRINT`` -- goal-introduced duplication must not be
  silently absorbed into "accepted" by a routine algo migration.
- ``nose-baseline.json`` (advisory; schema key UNCHANGED, only values migrate): the
  same survivor/vanished remap onto the flat accepted-fingerprint set.
- ``dup-review.json`` (overlay): a member-preserving REMAP of every ``code``-surface
  entry's ``id`` (v1 -> v2), preserving ``class``/``note``/``reviewed_at`` VERBATIM.
  An entry whose v1 id is not in the live scan is dropped with a logged note. This
  is NEVER a ``dup_review_lib.build_review`` re-seed (S4-D8's discipline).

Prints the one-shot collision assertion (``distinct(v2 fingerprints) ==
distinct(nose family ids)`` over the live scan, both counts); a mismatch exits
non-zero before anything is written -- an implementation-induced collision guard
(PQ1 already precludes a natural one under nose's global clustering).

Dry-run by default (prints the plan; writes nothing). ``--execute`` applies it. The
planning itself is pure (``migrate_dup_fingerprints_lib``); this CLI is the I/O shell
(adapter load, nose scan via ``dup_ratchet_scan.scan_families``, file read/write).
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
_plan = SKILL_RUNTIME.load_local_skill_module(__file__, "migrate_dup_fingerprints_lib")
_ratchet_baseline = SKILL_RUNTIME.load_local_skill_module(__file__, "dup_ratchet_baseline_lib")
_nose_baseline = SKILL_RUNTIME.load_local_skill_module(__file__, "nose_baseline_lib")
_dup_review = SKILL_RUNTIME.load_local_skill_module(__file__, "dup_review_lib")
_scan = SKILL_RUNTIME.load_local_skill_module(__file__, "dup_ratchet_scan")
_fingerprint = SKILL_RUNTIME.load_local_skill_module(__file__, "nose_fingerprint_lib")
_quality_adapter = SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.quality_adapter_lib")

DEFAULT_REVIEW_REL = "charness-artifacts/quality/dup-review.json"
DEFAULT_GATE_BASELINE_REL = "charness-artifacts/quality/dup-ratchet-baseline.json"
OLD_ALGO_VERSION = "1"
NEW_ALGO_VERSION = _fingerprint.FINGERPRINT_ALGO_VERSION


def _read_old_gate_ids(data) -> set[str] | None:
    """The pre-migration gate-baseline id set, reading EITHER the v2 flat
    ``code_family_fingerprints`` shape OR (idempotent re-run) the v3
    ``code_families`` shape. This tool is the one place allowed to read either
    shape, since its whole job is the v2->v3 transition; every other consumer
    reads v3 only (no dual-read, see ``dup_ratchet_baseline_lib``)."""
    v3_ids = _ratchet_baseline.load_gate_baseline_ids(data)
    if v3_ids is not None:
        return v3_ids
    if isinstance(data, dict):
        ids = data.get("code_family_fingerprints")
        if isinstance(ids, list):
            return {str(i) for i in ids if isinstance(i, str) and i}
    return None


def _enrich_live_scan(repo_root: Path, families: list[dict]) -> tuple[list[dict], list[str]]:
    """Compute BOTH v1 and v2 identity (+ v2 member hashes, + member files for the
    requires_review report) per live family. A family with an unreadable member span
    (either algo returns None) is excluded and its nose id logged -- never silently
    folded into the migration with a partial identity."""
    enriched: list[dict] = []
    unreadable: list[str] = []
    for family in families:
        v1_fp = _fingerprint.family_content_fingerprint(family, repo_root, algo=OLD_ALGO_VERSION)
        v2_fp = family.get("family_fingerprint")
        v2_hashes = family.get("family_member_hashes")
        nose_id = family.get("family_id") or family.get("id")
        if not v1_fp or not v2_fp or not isinstance(v2_hashes, list):
            unreadable.append(str(nose_id or "<no-id>"))
            continue
        files = sorted({
            loc.get("file") for loc in (family.get("locations") or [])
            if isinstance(loc, dict) and isinstance(loc.get("file"), str)
        })
        enriched.append({
            "v1": v1_fp, "v2": v2_fp, "member_hashes": [str(h) for h in v2_hashes],
            "nose_id": str(nose_id) if nose_id else None, "files": files,
        })
    return enriched, unreadable


def _requires_review_payload(gate_plan: dict, enriched: list[dict]) -> list[dict]:
    files_by_v2 = {entry["v2"]: entry["files"] for entry in enriched}
    return [
        {"v2_fingerprint": fp, "files": files_by_v2.get(fp, [])}
        for fp in gate_plan["requires_review"]
    ]


def build_report(repo_root: Path, config: dict, args) -> dict:
    scope_paths = list(args.scope_path or config.get("scope_paths") or [])
    if not scope_paths:
        return {"ok": False, "status": "no-scope-paths",
                "messages": ["no scope_paths configured (dup_ratchet.scope_paths) or passed "
                             "via --scope-path; refusing to scan nose DEFAULT_PATHS for a migration write."]}
    review_rel = config.get("review_artifact_path") or DEFAULT_REVIEW_REL
    gate_baseline_rel = config.get("gate_baseline_path") or DEFAULT_GATE_BASELINE_REL
    nose_baseline_rel = args.nose_baseline_path or _nose_baseline.DEFAULT_BASELINE_REL

    families, reason, live_version = _scan.scan_families(repo_root, scope_paths)
    if reason:
        return {"ok": False, "status": "scan-failed", "messages": [f"cannot compute live scan: {reason}"]}
    enriched, unreadable = _enrich_live_scan(repo_root, families or [])
    if unreadable:
        return {
            "ok": False, "status": "unreadable-members",
            "messages": [f"{len(unreadable)} live family(ies) had an unreadable member span; "
                         "fix or re-scope before migrating (never a partial migration)."],
            "unreadable_family_ids": unreadable,
        }
    collision = _plan.collision_report(enriched)
    if not collision["ok"]:
        return {"ok": False, "status": "collision-check-failed", "collision": collision,
                "messages": ["distinct v2 fingerprints != distinct nose family ids over the live "
                             "scan; refusing to migrate (implementation-induced collision, not a "
                             "corpus fact -- see PQ1)."]}

    old_gate_ids = _read_old_gate_ids(_scan.load_json(repo_root / gate_baseline_rel)) or set()
    gate_plan = _plan.plan_gate_baseline_migration(old_gate_ids, enriched, args.accept_new_family or [])
    old_nose_ids = _nose_baseline.load_baseline_ids(repo_root, nose_baseline_rel) or set()
    nose_plan = _plan.plan_advisory_baseline_migration(old_nose_ids, enriched)
    review_data = _scan.load_json(repo_root / review_rel) or {}
    review_entries = review_data.get("entries") if isinstance(review_data.get("entries"), list) else []
    review_plan = _plan.plan_review_migration(review_entries, enriched)

    return {
        "ok": True, "status": "planned", "mode": "execute" if args.execute else "dry-run",
        "collision": collision, "tool_version": live_version, "algo_version": NEW_ALGO_VERSION,
        "gate_baseline": {
            "path": gate_baseline_rel, "old_family_count": len(old_gate_ids),
            "survivor_count": len(gate_plan["survivors"]), "vanished": gate_plan["vanished"],
            "accepted_new": gate_plan["accepted_new"],
            "requires_review": _requires_review_payload(gate_plan, enriched),
            "new_family_count": len(gate_plan["new_members"]),
            "_new_members": gate_plan["new_members"],
        },
        "nose_baseline": {
            "path": nose_baseline_rel, "old_family_count": len(old_nose_ids),
            "survivor_count": len(nose_plan["survivors"]), "vanished": nose_plan["vanished"],
            "new_family_count": len(nose_plan["new_ids"]),
            "_new_ids": nose_plan["new_ids"],
        },
        "dup_review": {
            "path": review_rel, "code_entries_before": sum(1 for e in review_entries if isinstance(e, dict) and e.get("surface") == "code"),
            "dropped_ids": review_plan["dropped_ids"],
            "_entries": review_plan["entries"], "_note": review_data.get("note"),
        },
    }


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def apply_report(repo_root: Path, report: dict) -> list[str]:
    """Write the three migrated artifacts. Only called under --execute; the CLI
    keeps the dry-run report and the write step separate so a dry-run can never
    accidentally write."""
    messages = []
    gate = report["gate_baseline"]
    _write_json(repo_root / gate["path"], _ratchet_baseline.build_gate_baseline(
        gate["_new_members"], tool_version=report["tool_version"], algo_version=report["algo_version"],
    ))
    messages.append(f"wrote {gate['path']} ({gate['new_family_count']} families)")
    nose = report["nose_baseline"]
    _write_json(repo_root / nose["path"], _nose_baseline.build_baseline(
        nose["_new_ids"], tool_version=report["tool_version"], algo_version=report["algo_version"],
    ))
    messages.append(f"wrote {nose['path']} ({nose['new_family_count']} families)")
    review = report["dup_review"]
    new_review = {
        "schemaVersion": _dup_review.SCHEMA_VERSION,
        "note": review["_note"] or _dup_review.DEFAULT_NOTE,
        "fixable_ceiling": sum(1 for e in review["_entries"] if e.get("class") == "fixable"),
        "entries": sorted(review["_entries"], key=lambda e: (e.get("surface", ""), e.get("id", ""))),
    }
    errors = _dup_review.validate_review(new_review)
    if errors:
        raise RuntimeError("migrated dup-review.json failed validation: " + "; ".join(errors))
    _write_json(repo_root / review["path"], new_review)
    messages.append(f"wrote {review['path']} ({len(new_review['entries'])} entries)")
    return messages


def run(repo_root: Path, args) -> dict:
    adapter = _quality_adapter.load_quality_adapter_strict(repo_root)
    if adapter.get("errors"):
        return {"ok": False, "status": "adapter-invalid",
                "messages": ["quality adapter invalid: " + "; ".join(str(e) for e in adapter["errors"])]}
    config = adapter["data"].get("dup_ratchet") or {}
    report = build_report(repo_root, config, args)
    if report.get("ok") and args.execute:
        report["messages"] = apply_report(repo_root, report)
    return report


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Migrate the dup-ratchet fingerprints to a new algo version.")
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--scope-path", action="append", help="Override dup_ratchet.scope_paths (repeatable).")
    parser.add_argument("--nose-baseline-path", help="Override the advisory baseline path (default nose_baseline_lib.DEFAULT_BASELINE_REL).")
    parser.add_argument("--accept-new-family", action="append", metavar="V2_FINGERPRINT",
                         help="Accept one requires_review live family (by its v2 fingerprint) into the migrated gate baseline (repeatable).")
    parser.add_argument("--execute", action="store_true", help="Write the migrated artifacts (else dry-run: print the plan only).")
    parser.add_argument("--json", action="store_true")
    return parser.parse_args(argv)


def _print_human(report: dict) -> None:
    for message in report.get("messages", []):
        print(message)
    if not report.get("ok"):
        return
    print(f"mode={report['mode']} tool_version={report['tool_version']} algo_version={report['algo_version']}")
    collision = report["collision"]
    print(f"collision check: distinct v2 fingerprints={collision['distinct_v2_fingerprints']} "
          f"distinct nose family ids={collision['distinct_nose_family_ids']} ok={collision['ok']}")
    gate = report["gate_baseline"]
    print(f"gate baseline {gate['path']}: {gate['old_family_count']} old -> {gate['survivor_count']} survivor(s), "
          f"{len(gate['vanished'])} vanished, {len(gate['accepted_new'])} accepted-new, "
          f"{len(gate['requires_review'])} requires_review -> {gate['new_family_count']} new total")
    for candidate in gate["requires_review"]:
        print(f"  requires_review: {candidate['v2_fingerprint']} ({', '.join(candidate['files']) or 'no files'})")
    nose = report["nose_baseline"]
    print(f"nose baseline {nose['path']}: {nose['old_family_count']} old -> {nose['survivor_count']} survivor(s), "
          f"{len(nose['vanished'])} vanished -> {nose['new_family_count']} new total")
    review = report["dup_review"]
    print(f"dup-review {review['path']}: {review['code_entries_before']} code entries before, "
          f"{len(review['dropped_ids'])} dropped as orphaned")


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    repo_root = args.repo_root.resolve()
    report = run(repo_root, args)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        _print_human(report)
    return 0 if report.get("ok") else 1


if __name__ == "__main__":  # pragma: no cover - CLI entrypoint
    raise SystemExit(main())
