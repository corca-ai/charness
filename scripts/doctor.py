#!/usr/bin/env python3
# ruff: noqa: E402

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from scripts.control_plane_lib import (
    evaluate_version,
    load_manifests,
    now_iso,
    read_lock,
    run_check,
    support_state_for_manifest,
    upsert_lock,
)


def inspect_manifest(repo_root: Path, manifest: dict[str, object], *, write: bool) -> dict[str, object]:
    detect_result = run_check(manifest["checks"]["detect"], repo_root)
    healthcheck_result = run_check(manifest["checks"]["healthcheck"], repo_root) if detect_result["ok"] else {
        "ok": False,
        "results": [],
        "failure_details": ["detect failed; healthcheck skipped"],
        "failure_hint": manifest["checks"]["healthcheck"].get("failure_hint"),
    }
    version_result = evaluate_version(manifest, detect_result)
    support_state = support_state_for_manifest(manifest)
    previous_lock = read_lock(repo_root, manifest["tool_id"])

    if detect_result["ok"] and healthcheck_result["ok"]:
        doctor_status = "ok" if version_result["status"] in {"advisory", "matched", "unknown"} else "version-mismatch"
    elif not detect_result["ok"]:
        doctor_status = "missing"
    else:
        doctor_status = "unhealthy"

    payload = {
        "checked_at": now_iso(),
        "support_state": support_state,
        "detect": detect_result,
        "healthcheck": healthcheck_result,
        "version": version_result,
        "doctor_status": doctor_status,
    }
    if write:
        upsert_lock(repo_root, manifest, doctor=payload)
    return {**payload, "tool_id": manifest["tool_id"], "previous_lock_present": previous_lock is not None}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--tool-id", action="append", default=[])
    parser.add_argument("--write-locks", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    manifests = load_manifests(repo_root)
    selected = [manifest for manifest in manifests if not args.tool_id or manifest["tool_id"] in args.tool_id]
    results = [inspect_manifest(repo_root, manifest, write=args.write_locks) for manifest in selected]

    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        for result in results:
            print(f"{result['tool_id']}: {result['doctor_status']} ({result['support_state']})")

    if any(result["doctor_status"] in {"missing", "unhealthy", "version-mismatch"} for result in results):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
