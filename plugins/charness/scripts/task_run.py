"""Run one bounded Codex task in a clean, disposable Git worktree.

This is the execution half of the ``charness task`` surface.  The older
``claim``/``submit``/``review`` commands remain useful when a host already has
an external scheduler or carrier, but a normal implementation lane should not
need that state machine.  ``run_task`` owns the small set of facts that make a
lane reproducible: clean parent, explicit base, named branch, path scope,
external runtime paths, and a post-run receipt.
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Mapping, Sequence

from runtime_bootstrap import import_repo_module, runtime_root

_worktree = import_repo_module(__file__, "scripts.worktree_create_lib")
_exec = import_repo_module(__file__, "scripts.worktree_exec_lib")

PASS = "pass"
FAIL = "fail"
SCHEMA_VERSION = 1
_GIT_DISCOVERY_ENV = ("GIT_DIR", "GIT_COMMON_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE")
_BRANCH_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._/-]*$")
_SUSPICIOUS_RUNTIME_PARTS = frozenset(
    {
        ".pytest_cache",
        ".ruff_cache",
        "__pycache__",
        ".coverage",
        "coverage",
        "pytest-tmp",
        "tmp",
    }
)


class TaskRunError(ValueError):
    """A task-run preflight input is not safe or resolvable."""


def _git_env() -> dict[str, str]:
    return {key: value for key, value in os.environ.items() if key not in _GIT_DISCOVERY_ENV}


def _git(repo_root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=repo_root,
        env=_git_env(),
        check=False,
        capture_output=True,
        text=True,
    )


def _git_output(repo_root: Path, *args: str) -> str:
    result = _git(repo_root, *args)
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or "git command failed"
        raise TaskRunError(f"git {' '.join(args)} failed: {detail}")
    return result.stdout


def _require_git_root(repo_root: Path) -> Path:
    repo_root = repo_root.expanduser().resolve()
    discovered = Path(_git_output(repo_root, "rev-parse", "--show-toplevel").strip()).resolve()
    if discovered != repo_root:
        raise TaskRunError(
            f"--repo-root must be the Git worktree root, not a subdirectory: {repo_root}"
        )
    return repo_root


def _resolve_base_sha(repo_root: Path, base: str) -> str:
    if not base.strip():
        raise TaskRunError("--base is required and must resolve to a commit")
    result = _git(repo_root, "rev-parse", "--verify", "--quiet", "--end-of-options", f"{base}^{{commit}}")
    sha = result.stdout.strip()
    if result.returncode != 0 or not re.fullmatch(r"[0-9a-fA-F]{40,64}", sha):
        detail = result.stderr.strip() or f"ref is not resolvable: {base}"
        raise TaskRunError(detail)
    return sha


def _validate_branch(repo_root: Path, branch: str) -> str:
    if not branch or not _BRANCH_RE.fullmatch(branch) or ".." in branch or branch.endswith((".", "/")):
        raise TaskRunError(f"--branch is not a valid named branch: {branch!r}")
    result = _git(repo_root, "check-ref-format", "--branch", branch)
    if result.returncode != 0:
        raise TaskRunError(result.stderr.strip() or f"--branch is not a valid named branch: {branch}")
    return branch


def _normalize_scope(value: str) -> str:
    scope = value.strip()
    if scope.startswith("./"):
        scope = scope[2:]
    if (
        not scope
        or scope.startswith("/")
        or "\\" in scope
        or any(part in {"", ".", ".."} for part in scope.split("/"))
    ):
        raise TaskRunError(f"scope must be a repository-relative path: {value!r}")
    return scope


def normalize_scopes(scopes: Sequence[str]) -> list[str]:
    """Return one deterministic exact-path scope list."""
    if not scopes:
        raise TaskRunError("at least one --scope is required")
    return sorted({_normalize_scope(value) for value in scopes})


def _is_inside(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


def _validate_worktree_path(repo_root: Path, target_path: Path) -> Path:
    target = target_path.expanduser().resolve()
    if target == repo_root or _is_inside(target, repo_root):
        raise TaskRunError(f"worktree path must be outside the repository: {target}")
    if target.exists() or target.is_symlink():
        raise TaskRunError(f"worktree path already exists: {target}")
    return target


def _resolve_codex(value: str) -> str:
    if not value.strip():
        raise TaskRunError("--codex must name an executable")
    if "/" in value:
        candidate = Path(value).expanduser().resolve()
        if not candidate.is_file() or not os.access(candidate, os.X_OK):
            raise TaskRunError(f"Codex executable is not runnable: {value}")
        return str(candidate)
    resolved = shutil.which(value)
    if resolved is None:
        raise TaskRunError(f"Codex executable is not on PATH: {value}")
    return resolved


def _parse_nul_paths(output: str) -> list[str]:
    return sorted({entry for entry in output.split("\0") if entry})


def _collect_populations(repo_root: Path) -> dict[str, list[str]]:
    output = _git_output(
        repo_root,
        "status",
        "--porcelain=v1",
        "--untracked-files=all",
        "--ignored=matching",
        "-z",
    )
    populations: dict[str, list[str]] = {"tracked": [], "untracked": [], "ignored": []}
    records = output.split("\0")
    index = 0
    while index < len(records):
        record = records[index]
        index += 1
        if not record:
            continue
        if len(record) < 3:
            raise TaskRunError(f"unexpected git status record: {record!r}")
        status = record[:2]
        path = record[3:]
        if status == "??":
            populations["untracked"].append(path)
        elif status == "!!":
            populations["ignored"].append(path)
        else:
            populations["tracked"].append(path)
        # With porcelain -z, a rename's second pathname has no status prefix.
        # It is still useful in the receipt, so retain it as tracked evidence.
        if status[0] in {"R", "C"} and index < len(records) and records[index]:
            populations["tracked"].append(records[index])
            index += 1
    return {key: sorted(set(paths)) for key, paths in populations.items()}


def _snapshot_payload(snapshot: Mapping[str, Sequence[str]]) -> dict[str, Any]:
    return {
        key: {"count": len(paths), "paths": list(paths)}
        for key, paths in snapshot.items()
    }


def _population_delta(
    before: Mapping[str, Sequence[str]], after: Mapping[str, Sequence[str]], *, preflight: bool = False
) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for population in ("tracked", "untracked", "ignored"):
        before_set = set(before.get(population, ()))
        after_set = set(after.get(population, ()))
        added = sorted(after_set - before_set)
        removed = sorted(before_set - after_set)
        if preflight:
            verdict = PASS if population == "ignored" or not after_set else FAIL
            reason = (
                "ignored entries are reported as baseline residue"
                if population == "ignored"
                else "fresh worktrees must start without tracked or untracked changes"
            )
        elif population == "tracked":
            verdict = PASS
            reason = "tracked changes are the task candidate and remain inspectable"
        elif population == "untracked":
            # A new file is often the intended candidate (for example, a new
            # module or focused test).  The exact scope check below is the
            # single authority for whether it is allowed; do not add a second
            # blanket gate here that would reject normal implementations.
            verdict = PASS
            reason = (
                "new untracked files remain candidate changes; exact scope determines whether they are allowed"
                if added
                else "no new untracked files appeared during codex exec"
            )
        elif population == "ignored":
            # Ignored output cannot change the candidate diff. Keep it visible so
            # a cache leak is diagnosable, but do not turn a useful task receipt
            # into a failure merely because a repository has an ignored tool
            # directory. Standard runtime paths are routed out separately.
            verdict = "warn" if added else PASS
            reason = (
                "new ignored files appeared; inspect the generated-file causes"
                if added
                else "no new ignored files appeared during codex exec"
            )
        else:
            verdict = FAIL if added else PASS
            reason = (
                "new files appeared during codex exec"
                if added
                else "no new files appeared during codex exec"
            )
        result[population] = {
            "before_count": len(before_set),
            "after_count": len(after_set),
            "added": added,
            "removed": removed,
            "paths": sorted(after_set),
            "verdict": verdict,
            "reason": reason,
        }
    return result


def _changed_paths(repo_root: Path, base_sha: str) -> list[str]:
    tracked = _parse_nul_paths(
        _git_output(repo_root, "diff", "--no-renames", "--name-only", "-z", base_sha, "--")
    )
    untracked = _parse_nul_paths(_git_output(repo_root, "ls-files", "--others", "--exclude-standard", "-z", "--"))
    return sorted(set(tracked) | set(untracked))


def _scope_result(repo_root: Path, base_sha: str, scopes: Sequence[str], require_change: bool) -> dict[str, Any]:
    changed = _changed_paths(repo_root, base_sha)
    allowed = set(scopes)
    disallowed = sorted(path for path in changed if path not in allowed)
    if disallowed:
        verdict = FAIL
        reason = "candidate changes paths outside the exact declared scope"
    elif require_change and not changed:
        verdict = FAIL
        reason = "the task required a change but the worktree is unchanged"
    else:
        verdict = PASS
        reason = "all candidate changes are within the exact declared scope"
    return {
        "verdict": verdict,
        "reason": reason,
        "allowed_paths": list(scopes),
        "changed_paths": changed,
        "disallowed_paths": disallowed,
        "require_change": require_change,
    }


def _path_cause(path: str) -> str:
    parts = set(Path(path).parts)
    if path.endswith(".pyc") or parts & _SUSPICIOUS_RUNTIME_PARTS:
        return "runtime/cache output appeared inside the worktree; inspect PYTHONPYCACHEPREFIX, pytest cache, coverage, and TMPDIR"
    if "node_modules" in parts:
        return "dependency/install output appeared inside the worktree; compare with the prepare step"
    return "the child command produced a file outside the tracked task candidate; inspect the captured Codex log"


def _generated_files(
    populations: Mapping[str, Any], scopes: Sequence[str]
) -> list[dict[str, str]]:
    generated: list[dict[str, str]] = []
    allowed = set(scopes)
    for population in ("untracked", "ignored"):
        for path in populations[population].get("added", []):
            if population == "untracked" and path in allowed:
                classification = "candidate"
                cause = "new candidate path is within the exact declared scope"
            else:
                classification = "diagnostic"
                cause = _path_cause(path)
            generated.append(
                {
                    "population": population,
                    "path": path,
                    "classification": classification,
                    "cause": cause,
                }
            )
    return generated


def _task_id(branch: str, requested: str | None) -> str:
    raw = requested.strip() if requested else branch.replace("/", "-")
    value = re.sub(r"[^A-Za-z0-9._-]+", "-", raw).strip("-")
    return value[:96] or "task"


def _failure_payload(
    *, repo_root: Path | None, target_path: Path | None, task_id: str | None, error: str
) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "event": "task-run",
        "status": FAIL,
        "phase": "preflight",
        "repo_root": str(repo_root) if repo_root is not None else None,
        "worktree_path": str(target_path) if target_path is not None else None,
        "task_id": task_id,
        "error": error,
        "next_step": "Fix the preflight error, then rerun task run from a clean parent with an unused worktree path.",
    }


def _runtime_preview(target_path: Path) -> Path:
    preview_env = os.environ.copy()
    # A parent invocation may already carry an auto-selected runtime root for a
    # different checkout. Let the bootstrap choose a fresh worktree-keyed root.
    for key in ("CHARNESS_RUNTIME_ROOT", "CHARNESS_RUNTIME_ROOT_AUTO", "CHARNESS_RUNTIME_REPO_KEY"):
        preview_env.pop(key, None)
    return runtime_root(target_path, preview_env)


def _execute_codex(
    command: Sequence[str],
    *,
    target_path: Path,
    configured_env: Mapping[str, str],
    stdout_log: Path,
    stderr_log: Path,
    timeout_seconds: int,
) -> dict[str, Any]:
    result: dict[str, Any] = {"exit_code": None, "timed_out": False}
    try:
        with stdout_log.open("w", encoding="utf-8") as stdout_handle, stderr_log.open(
            "w", encoding="utf-8"
        ) as stderr_handle:
            completed = subprocess.run(
                command,
                cwd=target_path,
                env=dict(configured_env),
                stdout=stdout_handle,
                stderr=stderr_handle,
                check=False,
                timeout=timeout_seconds,
                text=True,
            )
            result["exit_code"] = completed.returncode
    except subprocess.TimeoutExpired:
        result["timed_out"] = True
    except OSError as exc:
        result["exec_error"] = str(exc)
    return result


def _completion_evidence(
    *,
    target_path: Path,
    parent_root: Path,
    before_exec: Mapping[str, Sequence[str]],
    base_sha: str,
    scopes: Sequence[str],
    require_change: bool,
    parent_before: Mapping[str, Sequence[str]],
) -> tuple[dict[str, Any], dict[str, Any], bool]:
    after_exec = _collect_populations(target_path)
    populations = _population_delta(before_exec, after_exec)
    scope = _scope_result(target_path, base_sha, scopes, require_change)
    parent_after = _collect_populations(parent_root)
    parent_unchanged = parent_after == parent_before
    evidence = {
        "after_exec": _snapshot_payload(after_exec),
        "populations": populations,
        "generated_files": _generated_files(populations, scopes),
        "scope": scope,
        "parent": {
            "unchanged": parent_unchanged,
            "before": _snapshot_payload(parent_before),
            "after": _snapshot_payload(parent_after),
            "verdict": PASS if parent_unchanged else FAIL,
        },
    }
    return evidence, scope, parent_unchanged


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
        resolved_repo = _require_git_root(repo_root)
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
            repo_root=resolved_repo or (repo_root.expanduser().resolve() if repo_root else None),
            target_path=resolved_target or target_path.expanduser().resolve(),
            task_id=task_id,
            error=str(exc),
        )

    payload: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
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
    if (
        execution["exit_code"] != 0
        or execution["timed_out"]
        or execution["exit_code"] is None
    ):
        blockers.append("codex execution did not exit successfully")
    if scope["verdict"] != PASS:
        blockers.append(scope["reason"])
    if not parent_unchanged:
        blockers.append("parent worktree changed while the task ran")
    if blockers:
        payload["status"] = FAIL
        payload["next_step"] = (
            "Inspect the retained worktree and captured logs; " + "; ".join(blockers) + "."
        )
    else:
        payload["status"] = PASS
        warnings = [
            f"{population}: {data['reason']}"
            for population, data in evidence["populations"].items()
            if data.get("verdict") == "warn"
        ]
        if warnings:
            payload["warnings"] = warnings
        payload["next_step"] = (
            f"Review the candidate in {resolved_target}; tracked changes are retained and the parent is unchanged."
        )
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
