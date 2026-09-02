#!/usr/bin/env python3
"""Release fresh-checkout probe checker, and the state vocabulary it answers in.

The key to read FIRST is ``status``. ``probe_results`` is NOT a reliable
"probes ran" signal on its own, and this docstring used to claim it was: the
key is also emitted empty by three branches that execute nothing (invalid
adapter, ``not_configured``, and the two ``blocked`` setup failures below), and
the clone-failure branch fills it with the CLONE's result, which is not a probe
result. A bounded review caught that claim one branch after the commit that
removed the same conflation from ``not_established``. Read ``status``:

- ``passed`` -> exit 0. The probes RAN and every one succeeded; ``probe_results``
  carries what each returned. A real answer.
- ``blocked`` -> exit 1. Something refused. That is usually a declared probe
  failing, but it also covers setup failures where NO probe ran -- a detached
  HEAD, or a clone that did not complete. Fail-closed either way, so it can stop
  a release it should not; distinguishing those is deferred, not solved.
- ``not_configured`` -> exit 0. The adapter declares no probes, so there is
  nothing to prove. A genuine opt-out, and it must never start refusing: a repo
  that legitimately declares nothing is answered, not stonewalled.
- ``not_established`` -> exit 3. Probes ARE declared and this invocation did not
  run them, so nothing about them was established. It carries NO
  ``probe_results`` key, because an empty result list is a verdict shape --
  "zero failures" -- for a run that produced no results at all.

``not_established`` used to be ``configured`` at exit 0, with ``probe_results:
[]``: a caller reading the byte could not tell "checked and clean" from "did not
check", inside a release gate. Exit 3 is ``run-quality.sh``'s
``UNESTABLISHED_EXIT``, which that runner renders UNPROVEN (counted in neither
the pass nor the fail column) for the labels that opted into it.

This checker does not run the probes on its own initiative. Execution is the
CALLER's spend to authorize (``--run-probes``; the release publish helper does it
before tag push), so a status listing never shells out to adapter-declared
commands a consumer repo wrote.
"""

from __future__ import annotations

import argparse
import runpy
import subprocess
import tempfile
from pathlib import Path
from types import SimpleNamespace
from typing import Any


def _load_skill_runtime_bootstrap():
    bootstrap = next(
        (
            ancestor / "skill_runtime_bootstrap.py"
            for ancestor in Path(__file__).resolve().parents
            if (ancestor / "skill_runtime_bootstrap.py").is_file()
        ),
        None,
    )
    if bootstrap is None:
        raise ImportError("skill_runtime_bootstrap.py not found")
    return SimpleNamespace(**runpy.run_path(str(bootstrap)))


SKILL_RUNTIME = _load_skill_runtime_bootstrap()
run_process = SKILL_RUNTIME.load_repo_module_from_skill_script(
    __file__, "scripts.subprocess_guard"
).run_process
yaml_output = SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.yaml_output")
_resolve_adapter = SKILL_RUNTIME.load_local_skill_module(__file__, "resolve_adapter")
load_adapter = _resolve_adapter.load_adapter
GIT_TIMEOUT_SECONDS = 120
FRESH_CHECKOUT_PROBE_TIMEOUT_SECONDS = 300
#: "Ran, established nothing" -- the same byte `run-quality.sh` reads as
#: UNESTABLISHED and renders UNPROVEN. Deliberately distinct from 1: no probe was
#: proven to fail, so this is not a blocker anyone can act on by fixing code; it
#: is a caller who asked for a listing and must ask again with `--run-probes` to
#: get a verdict.
UNESTABLISHED_EXIT = 3


def _run(command: list[str], *, cwd: Path) -> subprocess.CompletedProcess[str]:
    return run_process(command, cwd=cwd, timeout_seconds=GIT_TIMEOUT_SECONDS)


def _current_branch(repo_root: Path) -> str | None:
    result = _run(["git", "branch", "--show-current"], cwd=repo_root)
    branch = result.stdout.strip()
    return branch or None


def _run_shell(command: str, *, cwd: Path) -> dict[str, object]:
    result = run_process(
        command,
        cwd=cwd,
        shell=True,
        executable="/bin/bash",
        timeout_seconds=FRESH_CHECKOUT_PROBE_TIMEOUT_SECONDS,
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
        # No `probe_results` key. `probe_results: []` read as a verdict -- zero
        # failing probes -- for a run that executed none of them, and the status
        # word next to it (`configured`) named the ADAPTER's state, not this
        # run's. Both were exit 0, so a release preflight consulting this could
        # not tell "checked and clean" from "did not check".
        return {
            "status": "not_established",
            "reason": (
                "fresh_checkout_probes are declared but this invocation did not run them, "
                "so nothing was established about them"
            ),
            "remediation": (
                "Re-run with --run-probes for an established verdict, or read the release "
                "publish helper's own probe run (it executes them before tag push). "
                "This listing is not a pass."
            ),
            "fresh_checkout_probes": probes,
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
                "blockers": [
                    "fresh checkout probes require a named branch; detached HEAD is not supported"
                ],
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
    # This workflow owns bounded clone/probe subprocesses (120s for clone, 300s
    # per declared probe). Inheriting the shared 10s script default lets the
    # wrapper kill a valid fresh-checkout proof before those owners can report a
    # result. Keep explicit CHARNESS_SCRIPT_TIMEOUT_SECONDS overrides available,
    # but do not impose an unrelated aggregate default here.
    cancel_timeout = SKILL_RUNTIME.arm_cli_timeout(
        label="release fresh checkout probes", default_seconds=0
    )
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--repo-root",
        type=Path,
        required=True,
        help="Repo root used to resolve the release adapter",
    )
    parser.add_argument(
        "--run-probes",
        action="store_true",
        help="Clone the repo into a temp dir and execute the declared probes",
    )
    parser.add_argument(
        "--detail", action="store_true", help="Emit the full fresh-checkout probe payload as YAML"
    )
    try:
        args = parser.parse_args()
        payload = build_payload(args.repo_root.resolve(), run_probes=args.run_probes)
        if args.detail:
            yaml_output.emit_yaml(payload)
        else:
            print(f"fresh checkout probes: {payload['status']}")
            if remediation := payload.get("remediation"):
                print(f"- {remediation}")
            for blocker in payload.get("blockers", []):
                print(f"- {blocker}")
        if payload["status"] == "blocked":
            return 1
        if payload["status"] == "not_established":
            return UNESTABLISHED_EXIT
        return 0
    finally:
        cancel_timeout()


if __name__ == "__main__":
    raise SystemExit(main())
