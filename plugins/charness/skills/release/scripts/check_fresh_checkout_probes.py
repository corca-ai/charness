#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
import tempfile
from pathlib import Path
from typing import Any


def _load_skill_runtime_bootstrap():
    script_path = Path(__file__).resolve()
    for ancestor in script_path.parents:
        candidate = ancestor / "skill_runtime_bootstrap.py"
        if candidate.is_file():
            spec = importlib.util.spec_from_file_location("skill_runtime_bootstrap", candidate)
            if spec is None or spec.loader is None:
                continue
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module
    raise ImportError("skill_runtime_bootstrap.py not found")


SKILL_RUNTIME = _load_skill_runtime_bootstrap()
_resolve_adapter = SKILL_RUNTIME.load_local_skill_module(__file__, "resolve_adapter")
load_adapter = _resolve_adapter.load_adapter
GIT_TIMEOUT_SECONDS = 120
FRESH_CHECKOUT_PROBE_TIMEOUT_SECONDS = 300


def _run(command: list[str], *, cwd: Path) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            command,
            cwd=cwd,
            check=False,
            capture_output=True,
            text=True,
            timeout=GIT_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired as exc:
        return subprocess.CompletedProcess(
            command,
            124,
            str(exc.stdout or ""),
            f"timed out after {GIT_TIMEOUT_SECONDS}s",
        )


def _current_branch(repo_root: Path) -> str | None:
    result = _run(["git", "branch", "--show-current"], cwd=repo_root)
    branch = result.stdout.strip()
    return branch or None


def _run_shell(command: str, *, cwd: Path) -> dict[str, object]:
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            shell=True,
            executable="/bin/bash",
            check=False,
            capture_output=True,
            text=True,
            timeout=FRESH_CHECKOUT_PROBE_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired as exc:
        result = subprocess.CompletedProcess(
            command,
            124,
            str(exc.stdout or ""),
            f"timed out after {FRESH_CHECKOUT_PROBE_TIMEOUT_SECONDS}s",
        )
    return {
        "command": command,
        "returncode": result.returncode,
        "stdout_preview": result.stdout[:1000],
        "stderr_preview": result.stderr[:1000],
    }


def build_payload(repo_root: Path, *, run_probes: bool) -> dict[str, Any]:
    adapter = load_adapter(repo_root)
    if not adapter["valid"]:
        return {
            "status": "blocked",
            "reason": "release adapter is invalid",
            "fresh_checkout_probes": [],
            "probe_results": [],
            "blockers": [f"release adapter is invalid: {adapter['errors']}"],
        }
    probes = list(adapter["data"].get("fresh_checkout_probes", []))
    if not probes:
        return {
            "status": "not_configured",
            "reason": "release adapter declares no fresh_checkout_probes",
            "fresh_checkout_probes": [],
            "probe_results": [],
        }
    if not run_probes:
        return {
            "status": "configured",
            "reason": "fresh_checkout_probes are declared but were not run",
            "fresh_checkout_probes": probes,
            "probe_results": [],
        }

    with tempfile.TemporaryDirectory(prefix="charness-release-fresh-checkout-") as temp_dir:
        clone_path = Path(temp_dir) / "repo"
        clone_command = [
            "git",
            "clone",
            "--quiet",
            "--depth",
            "1",
        ]
        branch = _current_branch(repo_root)
        if not branch:
            return {
                "status": "blocked",
                "reason": "fresh checkout probes require a named branch",
                "fresh_checkout_probes": probes,
                "probe_results": [],
                "blockers": ["fresh checkout probes require a named branch; detached HEAD is not supported"],
            }
        clone_command.extend(["--branch", branch])
        clone_command.extend([repo_root.resolve().as_uri(), str(clone_path)])
        clone_result = _run(clone_command, cwd=repo_root)
        if clone_result.returncode != 0:
            return {
                "status": "blocked",
                "reason": "fresh checkout clone failed",
                "fresh_checkout_probes": probes,
                "blockers": [
                    "fresh checkout clone failed: "
                    f"exit {clone_result.returncode}; {clone_result.stderr[:400]}"
                ],
                "probe_results": [
                    {
                        "command": " ".join(clone_command[:-1] + ["<tempdir>"]),
                        "returncode": clone_result.returncode,
                        "stdout_preview": clone_result.stdout[:1000],
                        "stderr_preview": clone_result.stderr[:1000],
                    }
                ],
            }
        results = [_run_shell(command, cwd=clone_path) for command in probes]
    blockers = [
        (
            f"fresh checkout probe failed: `{result['command']}` exited {result['returncode']}; "
            f"stderr: {result['stderr_preview']}"
        )
        for result in results
        if result["returncode"] != 0
    ]
    return {
        "status": "blocked" if blockers else "passed",
        "reason": "declared fresh checkout probes executed",
        "fresh_checkout_probes": probes,
        "probe_results": results,
        "blockers": blockers,
    }


def main() -> int:
    cancel_timeout = SKILL_RUNTIME.arm_cli_timeout(label="release fresh checkout probes")
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True, help="Repository root used to resolve the release adapter")
    parser.add_argument("--run-probes", action="store_true", help="Clone the repo into a temp dir and execute the declared probes")
    parser.add_argument("--json", action="store_true", help="Emit JSON output")
    try:
        args = parser.parse_args()
        payload = build_payload(args.repo_root.resolve(), run_probes=args.run_probes)
        if args.json:
            print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
        else:
            print(f"fresh checkout probes: {payload['status']}")
            for blocker in payload.get("blockers", []):
                print(f"- {blocker}")
        return 1 if payload["status"] == "blocked" else 0
    finally:
        cancel_timeout()


if __name__ == "__main__":
    raise SystemExit(main())
