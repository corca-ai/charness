#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

from runtime_bootstrap import import_repo_module, repo_root_from_script

REPO_ROOT = repo_root_from_script(__file__)

_scripts_supply_chain_lib_module = import_repo_module(__file__, "scripts.supply_chain_lib")
ValidationError = _scripts_supply_chain_lib_module.ValidationError
detect_online_audit_surfaces = _scripts_supply_chain_lib_module.detect_online_audit_surfaces

DEFAULT_TRIAGE_OWNER = "repo-maintainers"


def online_command(tool: str, audit_level: str) -> list[str]:
    if tool == "npm":
        return ["npm", "audit", "--json", f"--audit-level={audit_level}"]
    if tool == "pnpm":
        return ["pnpm", "audit", "--json", f"--audit-level={audit_level}"]
    if tool == "uv":
        return ["uv", "audit", "--frozen"]
    raise ValidationError(f"unsupported online audit tool `{tool}`")


def run_surface(repo_root: Path, surface: dict[str, str], *, audit_level: str, triage_owner: str) -> dict[str, object]:
    tool = surface["tool"]
    binary = shutil.which(tool)
    if binary is None:
        raise ValidationError(
            f"online advisory requested for `{tool}` but the binary is missing; "
            f"install `{tool}` or skip the online audit. Triage owner: `{triage_owner}`."
        )
    command = online_command(tool, audit_level)
    completed = subprocess.run(command, cwd=repo_root, check=False, capture_output=True, text=True)
    return {
        "tool": tool,
        "surface": surface["surface"],
        "lockfile": surface["lockfile"],
        "binary": binary,
        "command": command,
        "network_dependency": "registry/service reachability required",
        "triage_owner": triage_owner,
        "exit_code": completed.returncode,
        "stdout": completed.stdout.strip(),
        "stderr": completed.stderr.strip(),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--audit-level", choices=("low", "moderate", "high", "critical"), default="high")
    parser.add_argument("--triage-owner", default=DEFAULT_TRIAGE_OWNER)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    surfaces = detect_online_audit_surfaces(repo_root)
    if not surfaces:
        message = (
            "No supported online supply-chain audit surfaces detected. "
            "This wrapper currently supports npm, pnpm, and uv dependency surfaces."
        )
        if args.json:
            print(json.dumps({"surfaces": [], "message": message}, ensure_ascii=False, indent=2))
        else:
            print(message)
        return 0

    results = [run_surface(repo_root, surface, audit_level=args.audit_level, triage_owner=args.triage_owner) for surface in surfaces]
    if args.json:
        print(json.dumps({"surfaces": results}, ensure_ascii=False, indent=2))
    else:
        for result in results:
            status = "PASS" if result["exit_code"] == 0 else "FAIL"
            rendered = " ".join(result["command"])
            print(
                f"{status} {result['tool']} online audit via `{rendered}` "
                f"(networked, triage owner `{result['triage_owner']}`)"
            )
    if any(result["exit_code"] != 0 for result in results):
        return 1
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except ValidationError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)
