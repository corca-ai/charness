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
needed). `--write-baseline` seeds the gate baseline from a full code scan.

Exit 0 when clean, inert, or degraded (overlay/baseline/nose missing => advisory,
never blocks). Exit 1 on a real block or an invalid adapter (fails closed).
"""

from __future__ import annotations

import argparse
import json
import runpy
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace


def _load_skill_runtime_bootstrap():
    bootstrap = next((ancestor / "skill_runtime_bootstrap.py" for ancestor in Path(__file__).resolve().parents if (ancestor / "skill_runtime_bootstrap.py").is_file()), None)
    if bootstrap is None:
        raise ImportError("skill_runtime_bootstrap.py not found")
    return SimpleNamespace(**runpy.run_path(str(bootstrap)))


SKILL_RUNTIME = _load_skill_runtime_bootstrap()
_ratchet = SKILL_RUNTIME.load_local_skill_module(__file__, "dup_ratchet_lib")
_inventory = SKILL_RUNTIME.load_local_skill_module(__file__, "inventory_nose_clones")
_nose_report = SKILL_RUNTIME.load_local_skill_module(__file__, "nose_report_lib")
_quality_adapter = SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.quality_adapter_lib")

DOC_INVENTORY = Path(__file__).resolve().parent / "inventory_doc_duplicates.py"
DEFAULT_REVIEW_REL = "charness-artifacts/quality/dup-review.json"
DEFAULT_GATE_BASELINE_REL = "charness-artifacts/quality/dup-ratchet-baseline.json"
# Full enumeration: high --top, no nose --baseline (the gate baseline seed must
# carry EVERY family_id, or unenumerated families false-block later).
FULL_SCAN_TOP = 1_000_000
FULL_SCAN_MIN_SIZE = 24


def _safe_read(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return None


def _load_json(path: Path):
    text = _safe_read(path)
    if text is None:
        return None
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None


def _families_from_text(text: str | None) -> list | None:
    if text is None:
        return None
    try:
        payload = json.loads(text) if text.strip() else {}
    except json.JSONDecodeError:
        return None
    if not isinstance(payload, dict):
        return None
    families = payload.get("families")
    return families if isinstance(families, list) else []


def _scan_code_family_ids(repo_root: Path, scope_paths: list[str]) -> tuple[set[str], str | None]:
    nose_bin = _inventory.resolve_nose_bin()
    if nose_bin is None:
        return set(), "nose binary not found; code clone scan skipped"
    paths = [str(path) for path in (scope_paths or _inventory.DEFAULT_PATHS)]
    # Full enumeration via the pinned `nose query` resolver: one query per root
    # (query takes one path), merged + deduped by family_id, high --top so every
    # family_id is recorded (a truncated seed would false-block later).
    result = _nose_report.collect_families(
        repo_root, nose_bin, paths, mode=_inventory.DEFAULT_MODE,
        min_size=FULL_SCAN_MIN_SIZE, top=FULL_SCAN_TOP, sort="extractability",
    )
    if result.get("status") == "error":
        return set(), f"nose code scan error: {result.get('stderr', '')[:160]}"
    ids = {
        _nose_report.family_identity(fam)
        for fam in result.get("families", [])
        if isinstance(fam, dict) and _nose_report.family_identity(fam)
    }
    return {fid for fid in ids if fid}, None


def _code_family_ids(args, repo_root: Path, scope_paths: list[str]) -> tuple[set[str], str | None]:
    if args.code_inventory is not None:
        families = _families_from_text(_safe_read(args.code_inventory))
        if families is None:
            return set(), f"injected code inventory unreadable ({args.code_inventory})"
        ids = {str(fam.get("family_id")) for fam in families if isinstance(fam, dict) and fam.get("family_id")}
        return ids, None
    return _scan_code_family_ids(repo_root, scope_paths)


def _run_doc_inventory(repo_root: Path) -> str:
    completed = subprocess.run(
        [sys.executable, str(DOC_INVENTORY), "--repo-root", str(repo_root), "--json"],
        cwd=repo_root, check=False, capture_output=True, text=True,
    )
    return completed.stdout


def _doc_drift_signatures(args, repo_root: Path) -> tuple[set[str], str | None]:
    if args.doc_inventory is not None:
        text = _safe_read(args.doc_inventory)
        if text is None:
            return set(), f"injected doc inventory missing ({args.doc_inventory})"
    else:
        text = _run_doc_inventory(repo_root)
    try:
        payload = json.loads(text) if text and text.strip() else {}
    except json.JSONDecodeError:
        return set(), "doc inventory JSON unreadable"
    if not isinstance(payload, dict):
        return set(), "doc inventory payload malformed"
    if payload.get("status") in {"missing", "version-too-old", "error"}:
        return set(), f"doc inventory degraded (status={payload.get('status')})"
    families = payload.get("families")
    if not isinstance(families, list):
        return set(), None
    signatures = {
        fam["signature"] for fam in families
        if isinstance(fam, dict) and isinstance(fam.get("signature"), str) and fam.get("signature")
    }
    return signatures, None


def _resolve_stagnation(repo_root: Path, review_rel: str, args) -> tuple[int | None, str | None, bool]:
    if args.stagnation is not None:
        return args.stagnation, "<injected>", True
    anchor = _ratchet.resolve_anchor(repo_root, review_rel)
    is_ancestor = _ratchet.anchor_is_ancestor(repo_root, anchor)
    stagnation = _ratchet.stagnation_commits(repo_root, anchor) if is_ancestor else None
    return stagnation, anchor, is_ancestor


def _write_baseline(repo_root: Path, config: dict, args) -> dict:
    scope_paths = list(config.get("scope_paths") or [])
    baseline_rel = config.get("gate_baseline_path") or DEFAULT_GATE_BASELINE_REL
    ids, reason = _code_family_ids(args, repo_root, scope_paths)
    if reason:
        return {"ok": False, "inert": False, "status": "write-baseline-failed",
                "messages": [f"cannot write gate baseline: {reason}"]}
    baseline = _ratchet.build_gate_baseline(ids)
    out = repo_root / baseline_rel
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(baseline, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {"ok": True, "inert": False, "status": "baseline-written",
            "code_family_count": len(ids), "gate_baseline_path": baseline_rel,
            "messages": [f"wrote gate baseline ({len(ids)} code family_ids) -> {baseline_rel}"]}


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
    overlay = _load_json(repo_root / review_rel)
    if overlay is None:
        degraded.append(f"overlay missing/unreadable ({review_rel})")
    baseline_ids = _ratchet.load_gate_baseline_ids(_load_json(repo_root / baseline_rel))
    if baseline_ids is None:
        degraded.append(f"gate baseline missing/unreadable ({baseline_rel})")
    code_ids, code_reason = _code_family_ids(args, repo_root, scope_paths)
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
    doc_signatures, doc_reason = _doc_drift_signatures(args, repo_root)
    if doc_reason:
        degraded.append(doc_reason)

    intentional_code, intentional_doc = _ratchet.overlay_intentional(overlay)
    stagnation, anchor, is_ancestor = _resolve_stagnation(repo_root, review_rel, args)
    verdict = _ratchet.evaluate(
        code_family_ids=code_ids, gate_baseline_ids=baseline_ids or set(),
        doc_drift_signatures=doc_signatures, intentional_code_ids=intentional_code,
        intentional_doc_signatures=intentional_doc,
        fixable_ceiling=_ratchet.overlay_fixable_ceiling(overlay),
        floor_F=floor_F, escalation_K=escalation_K, stagnation=stagnation,
        anchor=anchor, anchor_is_ancestor=is_ancestor, degraded_reasons=degraded,
    )
    verdict["inert"] = False
    return verdict


def run(repo_root: Path, args) -> dict:
    adapter = _quality_adapter.load_quality_adapter_strict(repo_root)
    if adapter.get("errors"):
        return {"ok": False, "inert": False, "status": "adapter-invalid",
                "adapter_errors": list(adapter["errors"]),
                "messages": ["quality adapter invalid: " + "; ".join(str(e) for e in adapter["errors"])]}
    config = adapter["data"].get("dup_ratchet") or {}
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
