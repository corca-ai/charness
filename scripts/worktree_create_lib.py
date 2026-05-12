from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

from runtime_bootstrap import import_repo_module

_doctor_lib = import_repo_module(__file__, "scripts.worktree_doctor_lib")

PASS = "pass"
WARN = "warn"
FAIL = "fail"


def _run_git(repo_root: Path, command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=repo_root, check=False, capture_output=True, text=True)


def _action(action_id: str, command: list[str], status: str, reason: str | None = None) -> dict[str, Any]:
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
        "next_action": message,
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
            "next_action": "Re-run without `--dry-run` to create the worktree and run readiness doctor.",
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

    doctor = _doctor_lib.run_doctor(target_path)
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
        "next_action": None,
    }
    if prepare:
        prepare_payload = _doctor_lib.run_prepare(target_path)
        payload["prepare"] = prepare_payload
        payload["doctor"] = prepare_payload.get("doctor", doctor)
        if prepare_payload.get("status") == PASS:
            payload["status"] = PASS
            payload["next_action"] = None
        else:
            payload["status"] = FAIL
            payload["next_action"] = prepare_payload.get("next_action") or "Fix prepare failures, then re-run `charness worktree prepare`."
        return payload

    if doctor.get("status") != PASS:
        payload["next_action"] = doctor.get("next_action") or f"Run `charness worktree prepare --repo-root {target_path}`."
    return payload


def render_create_text(payload: dict[str, Any]) -> str:
    lines = [
        f"target: {payload.get('target_path')}",
        f"status: {payload.get('status')}",
    ]
    if payload.get("dry_run"):
        lines.append("dry-run: true")
    branch = payload.get("branch")
    if branch:
        lines.append(f"branch: {branch}")
    base = payload.get("base")
    if base:
        lines.append(f"base: {base}")
    for action in payload.get("actions") or []:
        command = " ".join(action.get("command") or [])
        reason = f" -- {action['reason']}" if action.get("reason") else ""
        lines.append(f"{action['id']}: {action['status']} {command}{reason}".rstrip())
    doctor = payload.get("doctor")
    if isinstance(doctor, dict):
        lines.append(f"doctor: {doctor.get('status')}")
    prepare = payload.get("prepare")
    if isinstance(prepare, dict):
        lines.append(f"prepare: {prepare.get('status')}")
    if payload.get("error"):
        lines.append(f"error: {payload['error']}")
    if payload.get("next_action"):
        lines.append(f"next: {payload['next_action']}")
    return "\n".join(lines)


def emit_payload(payload: dict[str, Any], *, json_mode: bool) -> None:
    if json_mode:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(render_create_text(payload))
