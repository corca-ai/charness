"""Run one bounded Codex task in a clean, disposable Git worktree.

This is the execution half of the ``charness task`` surface.  ``run_task`` keeps
the orchestration small; Git, scope, runtime, and receipt calculations live in
``task_run_support`` so the public wrapper remains easy to audit.
"""

from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Sequence

from runtime_bootstrap import import_repo_module

_worktree = import_repo_module(__file__, "scripts.worktree_create_lib")
_exec = import_repo_module(__file__, "scripts.worktree_exec_lib")
try:
    from scripts import task_run_support as _support
except ModuleNotFoundError:
    import task_run_support as _support

PASS = _support.PASS
FAIL = _support.FAIL
TaskRunError = _support.TaskRunError
_collect_populations = _support._collect_populations
_completion_evidence = _support._completion_evidence
_execute_codex = _support._execute_codex
_failure_payload = _support._failure_payload
_git = _support._git
_git_output = _support._git_output
_population_delta = _support._population_delta
_resolve_base_sha = _support._resolve_base_sha
_resolve_codex = _support._resolve_codex
_runtime_preview = _support._runtime_preview
_snapshot_payload = _support._snapshot_payload
_task_id = _support._task_id
_validate_branch = _support._validate_branch
_validate_worktree_path = _support._validate_worktree_path
normalize_scopes = _support.normalize_scopes


def run_task(
    repo_root: Path,
    *,
    target_path: Path,
    branch: str,
    base: str,
    scopes: Sequence[str],
    prompt: str,
    codex: str = "codex",
    codex_args: Sequence[str] = (),
    task_id: str | None = None,
    prepare: bool = False,
    require_change: bool = False,
    timeout_seconds: int = 3600,
    dry_run: bool = False,
) -> dict[str, Any]:
    """Create, run, and receipt one bounded Codex worktree task."""
    resolved_repo: Path | None = None
    resolved_target: Path | None = None
    try:
        resolved_repo = _support._require_git_root(repo_root)
        parent_before = _collect_populations(resolved_repo)
        if any(parent_before[population] for population in ("tracked", "untracked")):
            raise TaskRunError(
                "parent worktree must be clean before launching a task; "
                "checkpoint current changes or choose a clean named worktree"
            )
        resolved_target = _validate_worktree_path(resolved_repo, target_path)
        resolved_branch = _validate_branch(resolved_repo, branch)
        normalized_scopes = normalize_scopes(scopes)
        if not prompt.strip():
            raise TaskRunError("--prompt or --prompt-file must contain non-empty instructions")
        base_sha = _resolve_base_sha(resolved_repo, base)
        codex_path = _resolve_codex(codex)
        if not isinstance(timeout_seconds, int) or timeout_seconds < 1:
            raise TaskRunError("--timeout-seconds must be a positive integer")
        resolved_task_id = _task_id(resolved_branch, task_id)
        preview_runtime = _runtime_preview(resolved_target)
        command = [codex_path, "exec", *codex_args, prompt]
    except (OSError, TaskRunError, subprocess.SubprocessError) as exc:
        return _failure_payload(
            repo_root=resolved_repo or repo_root.expanduser().resolve(),
            target_path=resolved_target or target_path.expanduser().resolve(),
            task_id=task_id,
            error=str(exc),
        )

    payload: dict[str, Any] = {
        "schema_version": _support.SCHEMA_VERSION,
        "event": "task-run",
        "status": FAIL,
        "phase": "planned" if dry_run else "create",
        "dry_run": dry_run,
        "task_id": resolved_task_id,
        "repo_root": str(resolved_repo),
        "worktree_path": str(resolved_target),
        "branch": resolved_branch,
        "base": base,
        "base_sha": base_sha,
        "scopes": normalized_scopes,
        "codex": {"executable": codex_path, "command": command[:-1] + ["<prompt>"]},
        "runtime_root": str(preview_runtime),
        "prepare": prepare,
        "require_change": require_change,
        "keep_worktree": True,
    }
    if dry_run:
        payload["status"] = PASS
        payload["next_step"] = "Re-run without --dry-run to create the named worktree and execute Codex."
        payload["actions"] = [
            {"id": "create-worktree", "status": "planned"},
            {"id": "codex-exec", "status": "planned", "cwd": str(resolved_target)},
        ]
        return payload

    started_at = time.monotonic()
    parent_before = _collect_populations(resolved_repo)
    resolved_target.parent.mkdir(parents=True, exist_ok=True)
    create_payload = _worktree.run_create(
        resolved_repo,
        target_path=resolved_target,
        branch=resolved_branch,
        base=base,
        prepare=prepare,
    )
    payload["create"] = create_payload
    payload["created"] = bool(create_payload.get("created"))
    if not create_payload.get("created") or (prepare and create_payload.get("status") != PASS):
        payload["phase"] = "create"
        payload["status"] = FAIL
        payload["next_step"] = create_payload.get("next_step") or "Fix worktree creation/doctor, then rerun task run."
        payload["parent"] = {"unchanged": _collect_populations(resolved_repo) == parent_before}
        return payload

    before_exec = _collect_populations(resolved_target)
    payload["before_exec"] = _snapshot_payload(before_exec)
    preflight_populations = _population_delta({}, before_exec, preflight=True)
    payload["preflight_populations"] = preflight_populations
    if any(preflight_populations[name]["verdict"] == FAIL for name in ("tracked", "untracked")):
        payload["phase"] = "preflight"
        payload["status"] = FAIL
        payload["next_step"] = "The newly-created worktree was not clean before Codex; inspect it and use a fresh path."
        payload["parent"] = {"unchanged": _collect_populations(resolved_repo) == parent_before}
        return payload

    child_env = os.environ.copy()
    for key in ("CHARNESS_RUNTIME_ROOT", "CHARNESS_RUNTIME_ROOT_AUTO", "CHARNESS_RUNTIME_REPO_KEY"):
        child_env.pop(key, None)
    configured_env = _exec.prepare_exec_environment(resolved_target, child_env)
    runtime_path = Path(configured_env["CHARNESS_RUNTIME_ROOT"])
    log_dir = runtime_path / "task-run" / resolved_task_id
    log_dir.mkdir(parents=True, exist_ok=True)
    stdout_log = log_dir / "codex.stdout.log"
    stderr_log = log_dir / "codex.stderr.log"
    payload["runtime_root"] = str(runtime_path)
    payload["logs"] = {"stdout": str(stdout_log), "stderr": str(stderr_log)}
    print(f"task run: executing Codex in {resolved_target}", file=sys.stderr)
    execution = _execute_codex(
        command,
        target_path=resolved_target,
        configured_env=configured_env,
        stdout_log=stdout_log,
        stderr_log=stderr_log,
        timeout_seconds=timeout_seconds,
    )
    if execution.get("exec_error"):
        payload["exec_error"] = execution["exec_error"]

    evidence, scope, parent_unchanged = _completion_evidence(
        target_path=resolved_target,
        parent_root=resolved_repo,
        before_exec=before_exec,
        base_sha=base_sha,
        scopes=normalized_scopes,
        require_change=require_change,
        parent_before=parent_before,
    )
    payload.update(
        {
            "phase": "complete",
            **execution,
            "duration_ms": int((time.monotonic() - started_at) * 1000),
            "target_sha": _git_output(resolved_target, "rev-parse", "HEAD").strip(),
            "target_branch": _git_output(resolved_target, "symbolic-ref", "--quiet", "--short", "HEAD").strip()
            if _git(resolved_target, "symbolic-ref", "--quiet", "--short", "HEAD").returncode == 0
            else None,
            **evidence,
        }
    )
    blockers: list[str] = []
    if execution["exit_code"] != 0 or execution["timed_out"] or execution["exit_code"] is None:
        blockers.append("codex execution did not exit successfully")
    if scope["verdict"] != PASS:
        blockers.append(scope["reason"])
    if not parent_unchanged:
        blockers.append("parent worktree changed while the task ran")
    if blockers:
        payload["status"] = FAIL
        payload["next_step"] = "Inspect the retained worktree and captured logs; " + "; ".join(blockers) + "."
    else:
        payload["status"] = PASS
        warnings = [
            f"{population}: {data['reason']}"
            for population, data in evidence["populations"].items()
            if data.get("verdict") == "warn"
        ]
        if warnings:
            payload["warnings"] = warnings
        payload["next_step"] = f"Review the candidate in {resolved_target}; tracked changes are retained and the parent is unchanged."
    print(f"task run: {payload['status']} ({resolved_task_id})", file=sys.stderr)
    return payload


def main() -> int:
    """Standalone diagnostic entrypoint; the canonical surface is ``charness task run``."""
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--path", dest="target_path", type=Path, required=True)
    parser.add_argument("--branch", required=True)
    parser.add_argument("--base", required=True)
    parser.add_argument("--scope", action="append", required=True)
    prompt = parser.add_mutually_exclusive_group(required=True)
    prompt.add_argument("--prompt")
    prompt.add_argument("--prompt-file", type=Path)
    parser.add_argument("--codex", default="codex")
    parser.add_argument("--codex-arg", action="append", default=[])
    parser.add_argument("--task-id")
    parser.add_argument("--prepare", action="store_true")
    parser.add_argument("--require-change", action="store_true")
    parser.add_argument("--timeout-seconds", type=int, default=3600)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    prompt_text = args.prompt
    if args.prompt_file is not None:
        prompt_text = args.prompt_file.read_text(encoding="utf-8")
    payload = run_task(
        args.repo_root,
        target_path=args.target_path,
        branch=args.branch,
        base=args.base,
        scopes=args.scope,
        prompt=prompt_text or "",
        codex=args.codex,
        codex_args=args.codex_arg,
        task_id=args.task_id,
        prepare=args.prepare,
        require_change=args.require_change,
        timeout_seconds=args.timeout_seconds,
        dry_run=args.dry_run,
    )
    from yaml_output import emit_yaml

    emit_yaml(payload)
    return 0 if payload.get("status") == PASS else 1


if __name__ == "__main__":
    raise SystemExit(main())
