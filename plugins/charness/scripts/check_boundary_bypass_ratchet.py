#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path

from runtime_bootstrap import import_repo_module, repo_root_from_script

REPO_ROOT = repo_root_from_script(__file__)

inventory_lib = import_repo_module(__file__, "scripts.inventory_boundary_bypass_lib")
ratchet_lib = import_repo_module(__file__, "scripts.boundary_bypass_ratchet_lib")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Enforce the boundary-bypass no-increase ratchet.")
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--baseline", type=Path, default=ratchet_lib.DEFAULT_BASELINE_PATH)
    parser.add_argument("--exemptions", type=Path, default=ratchet_lib.DEFAULT_EXEMPTIONS_PATH)
    parser.add_argument("--json", action="store_true", help="Emit the full ratchet report as JSON")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    baseline_path = (repo_root / args.baseline).resolve() if not args.baseline.is_absolute() else args.baseline
    exemptions_path = (repo_root / args.exemptions).resolve() if not args.exemptions.is_absolute() else args.exemptions
    try:
        baseline = ratchet_lib.load_baseline(baseline_path)
        exemptions = ratchet_lib.load_exemptions(exemptions_path)
        payload = inventory_lib.find_boundary_bypass_candidates(repo_root)
        report = ratchet_lib.check_payload(payload, baseline, exemptions)
    except ratchet_lib.RatchetError as exc:
        report = {"ok": False, "error": str(exc)}
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    elif report["ok"]:
        s = report["summary"]
        print(
            "boundary-bypass ratchet OK: "
            f"{s['candidate_count']} candidates, {s['convertible_count']} clean-convertible, "
            f"{s['internal_boundary_count']} internally-spawning, {s['keep_boundary_count']} likely keep-boundary"
        )
    else:
        print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
