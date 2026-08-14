#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path

from runtime_bootstrap import import_repo_module, repo_root_from_script
from yaml_output import emit_yaml

REPO_ROOT = repo_root_from_script(__file__)

inventory_lib = import_repo_module(__file__, "scripts.inventory_boundary_bypass_lib")
ratchet_lib = import_repo_module(__file__, "scripts.boundary_bypass_ratchet_lib")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Enforce the boundary-bypass no-increase ratchet.")
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--baseline", type=Path, default=ratchet_lib.DEFAULT_BASELINE_PATH)
    parser.add_argument("--exemptions", type=Path, default=ratchet_lib.DEFAULT_EXEMPTIONS_PATH)
    parser.add_argument("--write-baseline", action="store_true", help="Write a canonical baseline from the current inventory.")
    parser.add_argument("--confirm-baseline-delta", action="store_true", help="Confirm replacement of an existing baseline when --write-baseline changes it.")
    return parser.parse_args()


def _string_keys(value: object) -> set[str]:
    return set(value) if isinstance(value, list) and all(isinstance(item, str) for item in value) else set()


def baseline_delta(previous: object, proposed: dict) -> dict:
    """Render enough machine-readable state to review a guarded replacement."""
    previous_data = previous if isinstance(previous, dict) else {}
    previous_summary = previous_data.get("summary")
    return {
        "previous_metadata": {
            key: previous_data.get(key)
            for key in ("schemaVersion", "policy", "inventory_schemaVersion", "call_site_fingerprint_algo_version")
        },
        "proposed_metadata": {
            key: proposed.get(key)
            for key in ("schemaVersion", "policy", "inventory_schemaVersion", "call_site_fingerprint_algo_version")
        },
        "previous_summary": previous_summary if isinstance(previous_summary, dict) else None,
        "proposed_summary": proposed["summary"],
        "added_candidate_keys": sorted(_string_keys(proposed.get("candidate_keys")) - _string_keys(previous_data.get("candidate_keys"))),
        "removed_candidate_keys": sorted(_string_keys(previous_data.get("candidate_keys")) - _string_keys(proposed.get("candidate_keys"))),
    }


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    baseline_path = (repo_root / args.baseline).resolve() if not args.baseline.is_absolute() else args.baseline
    exemptions_path = (repo_root / args.exemptions).resolve() if not args.exemptions.is_absolute() else args.exemptions
    try:
        exemptions = ratchet_lib.load_exemptions(exemptions_path)
        payload = inventory_lib.find_boundary_bypass_candidates(repo_root)
        proposed = ratchet_lib.build_baseline(payload, exemptions)
        if args.write_baseline:
            previous = None
            if baseline_path.exists() and not baseline_path.is_file():
                raise ratchet_lib.RatchetError(f"{baseline_path}: baseline path must be a regular file")
            if baseline_path.is_file():
                try:
                    previous = json.loads(baseline_path.read_text(encoding="utf-8"))
                except json.JSONDecodeError as exc:
                    raise ratchet_lib.RatchetError(f"{baseline_path}: invalid JSON: {exc}") from exc
            changed = previous != proposed
            if changed and previous is not None and not args.confirm_baseline_delta:
                report = {
                    "ok": False,
                    "error": "baseline would change; rerun with --confirm-baseline-delta after reviewing the emitted baseline_delta",
                    "baseline_delta": baseline_delta(previous, proposed),
                }
            else:
                baseline_path.parent.mkdir(parents=True, exist_ok=True)
                temp_path = baseline_path.with_suffix(baseline_path.suffix + ".tmp")
                temp_path.write_text(json.dumps(proposed, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
                temp_path.replace(baseline_path)
                report = {"ok": True, "status": "baseline-written", "changed": changed, "summary": proposed["summary"]}
        else:
            baseline = ratchet_lib.load_baseline(baseline_path)
            report = ratchet_lib.check_payload(payload, baseline, exemptions)
    except ratchet_lib.RatchetError as exc:
        report = {"ok": False, "error": str(exc)}
    emit_yaml(report)
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
