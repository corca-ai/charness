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
    load_capabilities,
    now_iso,
    read_lock,
    run_check,
    upsert_lock,
)
from scripts.support_sync_lib import inspect_support_sync, support_state_for_manifest


def evaluate_readiness(manifest: dict[str, object], repo_root: Path) -> dict[str, object]:
    checks: list[dict[str, object]] = []
    for check in manifest.get("readiness_checks", []):
        result = run_check(check, repo_root)
        checks.append({"check_id": check["check_id"], "summary": check["summary"], **result})
    return {
        "ok": all(check["ok"] for check in checks),
        "checks": checks,
        "failed_checks": [check["check_id"] for check in checks if not check["ok"]],
    }


def inspect_manifest(repo_root: Path, manifest: dict[str, object], *, write: bool) -> dict[str, object]:
    detect_result = run_check(manifest["checks"]["detect"], repo_root)
    healthcheck_result = run_check(manifest["checks"]["healthcheck"], repo_root) if detect_result["ok"] else {
        "ok": False,
        "results": [],
        "failure_details": ["detect failed; healthcheck skipped"],
        "failure_hint": manifest["checks"]["healthcheck"].get("failure_hint"),
    }
    readiness_result = evaluate_readiness(manifest, repo_root)
    version_result = evaluate_version(manifest, detect_result)
    previous_lock = read_lock(repo_root, manifest["tool_id"])
    synced_strategy = None
    if previous_lock and isinstance(previous_lock.get("support"), dict):
        synced_strategy = previous_lock["support"].get("sync_strategy")
    support_state = support_state_for_manifest(manifest, sync_strategy=synced_strategy)
    support_sync = inspect_support_sync(repo_root, previous_lock)

    if support_sync["status"] == "missing":
        doctor_status = "support-missing"
    elif not detect_result["ok"]:
        doctor_status = "missing"
    elif not healthcheck_result["ok"]:
        doctor_status = "unhealthy"
    elif not readiness_result["ok"]:
        doctor_status = "not-ready"
    elif version_result["status"] not in {"advisory", "matched", "unknown"}:
        doctor_status = "version-mismatch"
    else:
        doctor_status = "ok"

    payload = {
        "checked_at": now_iso(),
        "kind": manifest["kind"],
        "access_modes": manifest["access_modes"],
        "capability_requirements": manifest.get("capability_requirements", {}),
        "support_state": support_state,
        "detect": detect_result,
        "healthcheck": healthcheck_result,
        "readiness": readiness_result,
        "version": version_result,
        "support_sync": support_sync,
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
    capabilities = load_capabilities(repo_root)
    selected = [capability for capability in capabilities if not args.tool_id or capability["tool_id"] in args.tool_id]
    results = [inspect_manifest(repo_root, capability, write=args.write_locks) for capability in selected]

    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        for result in results:
            print(f"{result['tool_id']}: {result['doctor_status']} ({result['support_state']})")

    if any(result["doctor_status"] in {"missing", "unhealthy", "not-ready", "version-mismatch", "support-missing"} for result in results):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
