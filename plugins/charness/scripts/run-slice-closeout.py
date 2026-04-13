#!/usr/bin/env python3
# ruff: noqa: E402

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from scripts.surfaces_lib import (
    SURFACES_PATH,
    SurfaceError,
    collect_changed_paths,
    load_surfaces,
    match_surfaces,
)


def run_command(repo_root: Path, command: str, phase: str) -> dict[str, object]:
    result = subprocess.run(
        ["/bin/bash", "-lc", command],
        cwd=repo_root,
        check=False,
        capture_output=True,
        text=True,
    )
    return {
        "phase": phase,
        "command": command,
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }


def print_text(payload: dict[str, object]) -> None:
    print(f"Closeout status: {payload['status']}")
    if payload["changed_paths"]:
        print("Changed paths:")
        for path in payload["changed_paths"]:
            print(f"- {path}")
    else:
        print("Changed paths: none")

    if payload["matched_surfaces"]:
        print("Matched surfaces:")
        for surface in payload["matched_surfaces"]:
            print(f"- {surface['surface_id']}: {surface['description']}")
    else:
        print("Matched surfaces: none")

    if payload["unmatched_paths"]:
        print("Unmatched paths:")
        for path in payload["unmatched_paths"]:
            print(f"- {path}")

    if payload["executed_commands"]:
        print("Executed commands:")
        for step in payload["executed_commands"]:
            status = "PASS" if step["returncode"] == 0 else "FAIL"
            print(f"- [{step['phase']}] {status} {step['command']}")
            if step["returncode"] != 0:
                if step["stdout"]:
                    print(step["stdout"], end="" if step["stdout"].endswith("\n") else "\n")
                if step["stderr"]:
                    print(step["stderr"], end="" if step["stderr"].endswith("\n") else "\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--surfaces-path", type=Path, default=SURFACES_PATH)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--paths", nargs="*", help="Explicit repo-relative paths. Defaults to current git diff.")
    parser.add_argument("--plan-only", action="store_true", help="Print obligations without executing commands.")
    parser.add_argument("--skip-sync", action="store_true")
    parser.add_argument("--skip-verify", action="store_true")
    parser.add_argument(
        "--allow-unmatched",
        action="store_true",
        help="Proceed even when changed files are not covered by the surfaces manifest.",
    )
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    manifest = load_surfaces(repo_root, surfaces_path=args.surfaces_path)
    assert manifest is not None
    changed_paths = args.paths if args.paths else collect_changed_paths(repo_root)
    payload = match_surfaces(manifest, changed_paths)
    payload["surfaces_manifest_path"] = manifest["path"]
    payload["executed_commands"] = []

    if not payload["changed_paths"]:
        payload["status"] = "noop"
        if args.json:
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            print_text(payload)
        return 0

    if payload["unmatched_paths"] and not args.allow_unmatched:
        payload["status"] = "blocked"
        message = (
            "changed paths are not covered by the surfaces manifest; "
            "add the missing coverage or rerun with --allow-unmatched"
        )
        payload["error"] = message
        if args.json:
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            print_text(payload)
            print(message, file=sys.stderr)
        return 1

    command_plan: list[tuple[str, str]] = []
    if not args.skip_sync:
        command_plan.extend(("sync", command) for command in payload["sync_commands"])
    if not args.skip_verify:
        command_plan.extend(("verify", command) for command in payload["verify_commands"])

    if args.plan_only:
        payload["status"] = "planned"
        payload["planned_commands"] = [
            {"phase": phase, "command": command} for phase, command in command_plan
        ]
        if args.json:
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            print_text(payload)
        return 0

    for phase, command in command_plan:
        result = run_command(repo_root, command, phase)
        payload["executed_commands"].append(result)
        if result["returncode"] != 0:
            payload["status"] = "failed"
            if args.json:
                print(json.dumps(payload, ensure_ascii=False, indent=2))
            else:
                print_text(payload)
            return 1

    payload["status"] = "completed"
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print_text(payload)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SurfaceError as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)
