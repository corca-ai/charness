#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from runtime_bootstrap import import_repo_module, repo_root_from_script

REPO_ROOT = repo_root_from_script(__file__)

_scripts_surfaces_lib_module = import_repo_module(__file__, "scripts.surfaces_lib")
SURFACES_PATH = _scripts_surfaces_lib_module.SURFACES_PATH
SurfaceError = _scripts_surfaces_lib_module.SurfaceError
collect_changed_paths = _scripts_surfaces_lib_module.collect_changed_paths
load_surfaces = _scripts_surfaces_lib_module.load_surfaces
match_surfaces = _scripts_surfaces_lib_module.match_surfaces
_scripts_plan_cautilus_proof_module = import_repo_module(__file__, "scripts.plan_cautilus_proof")
plan_cautilus_proof = _scripts_plan_cautilus_proof_module.plan_cautilus_proof


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

    cautilus_plan = payload.get("cautilus_plan")
    if isinstance(cautilus_plan, dict) and cautilus_plan.get("required"):
        print("Cautilus proof:")
        print(f"- run_mode: {cautilus_plan['run_mode']}")
        print(f"- proof_kinds: {', '.join(cautilus_plan['proof_kinds'])}")
        print(f"- next_action: {cautilus_plan['next_action']}")
        for note in cautilus_plan.get("notes", []):
            print(f"- note: {note}")

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

    cautilus_plan = plan_cautilus_proof(repo_root, payload["changed_paths"])
    payload["cautilus_plan"] = cautilus_plan
    if cautilus_plan["required"] and not cautilus_plan["artifact_changed"]:
        payload["status"] = "blocked"
        payload["error"] = (
            f"cautilus proof is required for this slice; next_action=`{cautilus_plan['next_action']}` "
            f"and `{cautilus_plan['artifact_path']}` is not refreshed yet"
        )
        if args.json:
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            print_text(payload)
            print(payload["error"], file=sys.stderr)
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
