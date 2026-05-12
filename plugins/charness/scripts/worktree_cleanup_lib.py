from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

from runtime_bootstrap import import_repo_module

_audit_lib = import_repo_module(__file__, "scripts.worktree_audit_lib")

PASS = "pass"
FAIL = "fail"


def _run_git(repo_root: Path, *args: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=cwd or repo_root,
        check=False,
        capture_output=True,
        text=True,
    )


def _short_branch(ref: str | None) -> str | None:
    if not ref:
        return None
    prefix = "refs/heads/"
    return ref[len(prefix) :] if ref.startswith(prefix) else ref


def _find_entry(entries: list[dict[str, Any]], target_path: Path) -> dict[str, Any] | None:
    target = target_path.resolve()
    for entry in entries:
        if Path(entry["path"]).resolve() == target:
            return entry
    return None


def _is_dirty(path: Path) -> tuple[bool, str]:
    result = _run_git(path, "status", "--porcelain", cwd=path)
    if result.returncode != 0:
        return True, result.stderr.strip() or "git status failed"
    return bool(result.stdout.strip()), result.stdout.strip()


def _branch_is_contained(repo_root: Path, branch: str, base: str) -> tuple[bool, str]:
    branch_ref = f"refs/heads/{branch}"
    result = _run_git(repo_root, "merge-base", "--is-ancestor", branch_ref, base)
    if result.returncode == 0:
        return True, ""
    if result.returncode == 1:
        return False, f"{branch_ref} is not contained in {base}"
    return False, result.stderr.strip() or f"could not compare {branch_ref} to {base}"


def _action(action_id: str, command: list[str], status: str, reason: str | None = None) -> dict[str, Any]:
    payload: dict[str, Any] = {"id": action_id, "command": command, "status": status}
    if reason:
        payload["reason"] = reason
    return payload


def _fail(repo_root: Path, target_path: Path, message: str, *, actions: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    return {
        "status": FAIL,
        "repo_root": str(repo_root),
        "target_path": str(target_path),
        "dry_run": True,
        "actions": actions or [],
        "error": message,
        "next_action": message,
    }


def _resolve_cleanup_target(
    repo_root: Path,
    target_path: Path,
    *,
    force: bool,
) -> tuple[dict[str, Any] | None, Path | None, dict[str, Any] | None, bool, str]:
    audit = _audit_lib.run_audit(repo_root)
    if audit.get("status") == FAIL:
        return None, None, _fail(repo_root, target_path, audit.get("error") or "worktree audit failed"), False, ""

    primary_worktree = Path(audit["primary_worktree"]).resolve()
    entry = _find_entry(audit.get("entries", []), target_path)
    if entry is None:
        return None, primary_worktree, _fail(primary_worktree, target_path, "target path is not registered as a git worktree"), False, ""
    if primary_worktree == target_path:
        return None, primary_worktree, _fail(primary_worktree, target_path, "refusing to remove the primary worktree"), False, ""
    if entry.get("prunable") or not target_path.exists():
        return (
            None,
            primary_worktree,
            _fail(
                primary_worktree,
                target_path,
                "target worktree path is missing or prunable; run `charness worktree audit --prune` instead",
            ),
            False,
            "",
        )

    dirty, dirty_detail = _is_dirty(target_path)
    if dirty and not force:
        return (
            None,
            primary_worktree,
            _fail(
                primary_worktree,
                target_path,
                "target worktree has uncommitted changes; commit, stash, or pass `--force`",
            ),
            dirty,
            dirty_detail,
        )
    return entry, primary_worktree, None, dirty, dirty_detail


def _plan_cleanup_actions(
    repo_root: Path,
    target_path: Path,
    *,
    branch: str | None,
    delete_merged_branch: bool,
    branch_base: str,
    force: bool,
) -> tuple[list[dict[str, Any]], dict[str, Any] | None]:
    actions: list[dict[str, Any]] = []
    remove_command = ["git", "worktree", "remove"]
    if force:
        remove_command.append("--force")
    remove_command.append(str(target_path))
    actions.append(_action("remove-worktree", remove_command, "planned"))

    if delete_merged_branch:
        if branch is None:
            actions.append(_action("delete-branch", [], "skipped", "target worktree is detached"))
        else:
            contained, reason = _branch_is_contained(repo_root, branch, branch_base)
            if not contained:
                return (
                    actions,
                    _fail(repo_root, target_path, f"refusing to delete branch {branch!r}: {reason}", actions=actions),
                )
            actions.append(_action("delete-branch", ["git", "branch", "-D", branch], "planned"))

    actions.append(_action("prune-metadata", ["git", "worktree", "prune"], "planned"))
    return actions, None


def _execute_actions(
    repo_root: Path,
    actions: list[dict[str, Any]],
) -> dict[str, Any] | None:
    for action in actions:
        if action["status"] == "skipped":
            continue
        command = action["command"]
        result = subprocess.run(
            command,
            cwd=repo_root,
            check=False,
            capture_output=True,
            text=True,
        )
        action["exit_code"] = result.returncode
        if result.stdout.strip():
            action["stdout"] = result.stdout.strip()
        if result.stderr.strip():
            action["stderr"] = result.stderr.strip()
        if result.returncode != 0:
            action["status"] = "failed"
            return action
        action["status"] = "done"
    return None


def run_cleanup(
    repo_root: Path,
    *,
    target_path: Path,
    delete_merged_branch: bool = False,
    branch_base: str = "HEAD",
    yes: bool = False,
    force: bool = False,
) -> dict[str, Any]:
    repo_root = repo_root.resolve()
    target_path = target_path.resolve()

    entry, operation_root, failure, dirty, dirty_detail = _resolve_cleanup_target(repo_root, target_path, force=force)
    if failure is not None:
        return failure
    assert entry is not None
    assert operation_root is not None
    branch = _short_branch(entry.get("branch"))
    actions, plan_failure = _plan_cleanup_actions(
        operation_root,
        target_path,
        branch=branch,
        delete_merged_branch=delete_merged_branch,
        branch_base=branch_base,
        force=force,
    )
    if plan_failure is not None:
        plan_failure.setdefault("requested_repo_root", str(repo_root))
        return plan_failure

    if yes:
        failed_action = _execute_actions(operation_root, actions)
        if failed_action is not None:
            return {
                "status": FAIL,
                "repo_root": str(operation_root),
                "requested_repo_root": str(repo_root),
                "target_path": str(target_path),
                "branch": branch,
                "branch_base": branch_base,
                "dirty": dirty,
                "dirty_detail": dirty_detail,
                "dry_run": False,
                "actions": actions,
                "error": f"{failed_action['id']} failed",
                "next_action": f"Inspect action {failed_action['id']} and retry cleanup when safe.",
            }

    return {
        "status": PASS,
        "repo_root": str(operation_root),
        "requested_repo_root": str(repo_root),
        "target_path": str(target_path),
        "branch": branch,
        "branch_base": branch_base,
        "dirty": dirty,
        "dirty_detail": dirty_detail if dirty else "",
        "dry_run": not yes,
        "actions": actions,
        "next_action": None if yes else "Re-run with `--yes` to execute the planned cleanup actions.",
    }


def render_cleanup_text(payload: dict[str, Any]) -> str:
    lines = [
        f"target: {payload.get('target_path')}",
        f"status: {payload.get('status')}",
    ]
    if payload.get("dry_run"):
        lines.append("dry-run: true")
    branch = payload.get("branch")
    if branch:
        lines.append(f"branch: {branch} (base={payload.get('branch_base')})")
    if payload.get("error"):
        lines.append(f"error: {payload['error']}")
    for action in payload.get("actions") or []:
        command = " ".join(action.get("command") or [])
        reason = f" — {action['reason']}" if action.get("reason") else ""
        lines.append(f"{action['id']}: {action['status']} {command}{reason}".rstrip())
    if payload.get("next_action"):
        lines.append(f"next: {payload['next_action']}")
    return "\n".join(lines)


def emit_payload(payload: dict[str, Any], *, json_mode: bool) -> None:
    if json_mode:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(render_cleanup_text(payload))
