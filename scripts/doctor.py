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
    load_capabilities,
    now_iso,
    upsert_lock,
)
from scripts.doctor_lib import inspect_capability_state
from scripts.install_provenance_lib import detect_install_provenance
from scripts.upstream_release_lib import probe_release


def inspect_manifest(repo_root: Path, manifest: dict[str, object], *, write: bool) -> dict[str, object]:
    state = inspect_capability_state(repo_root, manifest)
    provenance_result = detect_install_provenance(manifest)
    provenance_result["checked_at"] = now_iso()
    payload = {
        "checked_at": now_iso(),
        **state,
        "provenance": provenance_result,
    }
    release = probe_release(manifest)
    if release is not None:
        payload["release"] = release
    if write:
        lock_payload = dict(payload)
        lock_payload.pop("previous_lock_present", None)
        lock_payload.pop("release", None)
        lock_payload.pop("provenance", None)
        upsert_lock(repo_root, manifest, doctor=lock_payload, release=release, provenance=provenance_result)
    return {**payload, "tool_id": manifest["tool_id"], "previous_lock_present": state["previous_lock_present"]}


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
