from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any

from runtime_bootstrap import import_repo_module

_subprocess_guard = import_repo_module(__file__, "scripts.core.subprocess_guard")
run_process = _subprocess_guard.run_process

_doctor_lib = import_repo_module(__file__, "scripts.worktree_doctor_lib")

PASS = "pass"
WARN = "warn"
FAIL = "fail"


def _run_git(repo_root: Path, command: list[str]) -> subprocess.CompletedProcess[str]:
    return run_process(command, cwd=repo_root, timeout_seconds=None)


def _action(
    action_id: str, command: list[str], status: str, reason: str | None = None
) -> dict[str, Any]:
    payload: dict[str, Any] = {"id": action_id, "command": command, "status": status}
    if reason:
        payload["reason"] = reason
    return payload


def _create_command(
    target_path: Path,
    *,
    branch: str | None,
    base: str | None,
    detach: bool,
    force: bool,
) -> list[str]:
    command = ["git", "worktree", "add"]
    if force:
        command.append("--force")
    if detach:
        command.append("--detach")
    elif branch:
        command.extend(["-b", branch])
    command.append(str(target_path))
    if base:
        command.append(base)
    return command


def _fail(
    repo_root: Path,
    target_path: Path,
    message: str,
    *,
    actions: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    return {
        "status": FAIL,
        "repo_root": str(repo_root),
        "target_path": str(target_path),
        "dry_run": False,
        "created": False,
        "actions": actions or [],
        "error": message,
        "next_step": message,
    }


def run_create(
    repo_root: Path,
    *,
    target_path: Path,
    branch: str | None = None,
    base: str | None = None,
    detach: bool = False,
    prepare: bool = False,
    dry_run: bool = False,
    force: bool = False,
) -> dict[str, Any]:
    repo_root = repo_root.resolve()
    target_path = target_path.resolve()
    if branch and detach:
        return _fail(repo_root, target_path, "`--branch` and `--detach` cannot be used together.")

    command = _create_command(target_path, branch=branch, base=base, detach=detach, force=force)
    create_action = _action("create-worktree", command, "planned" if dry_run else "running")
    actions = [create_action]
    if dry_run:
        return {
            "status": PASS,
            "repo_root": str(repo_root),
            "target_path": str(target_path),
            "branch": branch,
            "base": base,
            "detach": detach,
            "dry_run": True,
            "created": False,
            "actions": actions,
            "next_step": "Re-run without `--dry-run` to create the worktree and run readiness doctor.",
        }

    result = _run_git(repo_root, command)
    create_action["exit_code"] = result.returncode
    if result.stdout.strip():
        create_action["stdout"] = result.stdout.strip()
    if result.stderr.strip():
        create_action["stderr"] = result.stderr.strip()
    if result.returncode != 0:
        create_action["status"] = "failed"
        return _fail(
            repo_root,
            target_path,
            result.stderr.strip() or result.stdout.strip() or "git worktree add failed",
            actions=actions,
        )
    create_action["status"] = "done"

    # `require_isolation=True` unconditionally: this function JUST created a
    # linked worktree, so the check must pass, and asserting it here is what
    # turns SC10's flag from something an agent has to remember to type into
    # part of the mechanism. A round-1 reviewer found the flag had no production
    # caller at all -- enforcement exactly as strong as the prose rule it
    # replaced, minus the prose. If this ever fails, `git worktree add` returned
    # something that is not an isolated checkout, which is worth a loud WARN.
    doctor = _doctor_lib.run_doctor(target_path, require_isolation=True)
    payload: dict[str, Any] = {
        "status": PASS if doctor.get("status") == PASS else WARN,
        "repo_root": str(repo_root),
        "target_path": str(target_path),
        "branch": branch,
        "base": base,
        "detach": detach,
        "dry_run": False,
        "created": True,
        "actions": actions,
        "doctor": doctor,
        "_checkout": doctor.get("_checkout"),
        "next_step": None,
    }
    if prepare:
        # Carries the SAME requirement as the doctor call above. Without it the
        # prepare payload -- which replaces `payload["doctor"]` and recomputes
        # `payload["status"]` on the next two lines -- was produced by a doctor
        # run that did not require isolation, silently erasing the verdict on the
        # prescribed `--prepare` path.
        prepare_payload = _doctor_lib.run_prepare(
            target_path,
            require_isolation=True,
            pre_doctor=doctor,
        )
        payload["prepare"] = prepare_payload
        payload["doctor"] = prepare_payload.get("doctor", doctor)
        updated_doctor = payload["doctor"]
        payload["_checkout"] = (
            updated_doctor.get("_checkout") if isinstance(updated_doctor, dict) else None
        )
        if prepare_payload.get("status") == PASS:
            payload["status"] = PASS
            payload["next_step"] = None
        else:
            payload["status"] = FAIL
            payload["next_step"] = (
                prepare_payload.get("next_step")
                or "Fix prepare failures, then re-run `charness worktree prepare`."
            )
        return payload

    if doctor.get("status") != PASS:
        payload["next_step"] = (
            doctor.get("next_step") or f"Run `charness worktree prepare --repo-root {target_path}`."
        )
    return payload
