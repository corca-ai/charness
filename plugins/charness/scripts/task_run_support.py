"""Git, scope, runtime, and receipt helpers for :mod:`task_run`."""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Mapping, Sequence

import yaml

from runtime_bootstrap import runtime_root

PASS = "pass"
FAIL = "fail"
SCHEMA_VERSION = 1
TASK_MODEL = "gpt-5.6-luna"
TASK_EFFORTS = ("medium", "xhigh", "max")
_GIT_DISCOVERY_ENV = ("GIT_DIR", "GIT_COMMON_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE")
_BRANCH_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._/-]*$")
_SUSPICIOUS_RUNTIME_PARTS = frozenset(
    {".pytest_cache", ".ruff_cache", "__pycache__", ".coverage", "coverage", "pytest-tmp", "tmp"}
)


class TaskRunError(ValueError):
    """A task-run preflight input is not safe or resolvable."""


def _git_env() -> dict[str, str]:
    return {key: value for key, value in os.environ.items() if key not in _GIT_DISCOVERY_ENV}


def _git(repo_root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args], cwd=repo_root, env=_git_env(), check=False,
        capture_output=True, text=True,
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
        raise TaskRunError(f"--repo-root must be the Git worktree root, not a subdirectory: {repo_root}")
    return repo_root


def _resolve_base_sha(repo_root: Path, base: str) -> str:
    if not base.strip():
        raise TaskRunError("--base is required and must resolve to a commit")
    result = _git(repo_root, "rev-parse", "--verify", "--quiet", "--end-of-options", f"{base}^{{commit}}")
    sha = result.stdout.strip()
    if result.returncode != 0 or not re.fullmatch(r"[0-9a-fA-F]{40,64}", sha):
        raise TaskRunError(result.stderr.strip() or f"ref is not resolvable: {base}")
    return sha


def _git_common_dir(repo_root: Path) -> Path:
    """Writable Git administration root required for commits from a linked worktree."""
    value = _git_output(repo_root, "rev-parse", "--git-common-dir").strip()
    common = Path(value)
    if not common.is_absolute():
        common = repo_root / common
    resolved = common.resolve()
    if not resolved.is_dir():
        raise TaskRunError(f"Git common directory is not a directory: {resolved}")
    return resolved


def _git_dir(repo_root: Path) -> Path:
    """Return the checkout-specific Git administration directory."""
    value = _git_output(repo_root, "rev-parse", "--git-dir").strip()
    git_dir = Path(value)
    if not git_dir.is_absolute():
        git_dir = repo_root / git_dir
    resolved = git_dir.resolve()
    if not resolved.is_dir():
        raise TaskRunError(f"Git directory is not a directory: {resolved}")
    return resolved


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
    if not scope or scope.startswith("/") or "\\" in scope or any(
        part in {"", ".", ".."} for part in scope.split("/")
    ):
        raise TaskRunError(f"scope must be a repository-relative path: {value!r}")
    return scope


def normalize_scopes(scopes: Sequence[str]) -> list[str]:
    """Return one deterministic repository-relative scope list."""
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
        repo_root, "status", "--porcelain=v1", "--untracked-files=all", "--ignored=matching", "-z"
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
        status, path = record[:2], record[3:]
        if status == "??":
            populations["untracked"].append(path)
        elif status == "!!":
            populations["ignored"].append(path)
        else:
            populations["tracked"].append(path)
        if status[0] in {"R", "C"} and index < len(records) and records[index]:
            populations["tracked"].append(records[index])
            index += 1
    return {key: sorted(set(paths)) for key, paths in populations.items()}


def _snapshot_payload(snapshot: Mapping[str, Sequence[str]]) -> dict[str, Any]:
    return {key: {"count": len(paths), "paths": list(paths)} for key, paths in snapshot.items()}


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
            reason = "ignored entries are reported as baseline residue" if population == "ignored" else "fresh worktrees must start without tracked or untracked changes"
        elif population == "tracked":
            verdict, reason = PASS, "tracked changes are the task candidate and remain inspectable"
        elif population == "untracked":
            verdict = PASS
            reason = "new untracked files remain candidate changes; exact scope determines whether they are allowed" if added else "no new untracked files appeared during codex exec"
        else:
            verdict = "warn" if added else PASS
            reason = "new ignored files appeared; inspect the generated-file causes" if added else "no new ignored files appeared during codex exec"
        result[population] = {
            "before_count": len(before_set), "after_count": len(after_set), "added": added,
            "removed": removed, "paths": sorted(after_set), "verdict": verdict, "reason": reason,
        }
    return result


def _changed_paths(repo_root: Path, base_sha: str) -> list[str]:
    tracked = _parse_nul_paths(_git_output(repo_root, "diff", "--no-renames", "--name-only", "-z", base_sha, "--"))
    untracked = _parse_nul_paths(_git_output(repo_root, "ls-files", "--others", "--exclude-standard", "-z", "--"))
    return sorted(set(tracked) | set(untracked))
def _is_glob_scope(scope: str) -> bool:
    return any(marker in scope for marker in ("*", "?", "[", "]"))


def _validate_glob_scope(scope: str) -> None:
    index = 0
    while index < len(scope):
        marker = scope[index]
        if marker == "]":
            raise TaskRunError(f"scope glob has an unmatched ']': {scope!r}")
        if marker != "[":
            index += 1
            continue
        close = scope.find("]", index + 1)
        minimum = index + 2 if scope[index + 1:index + 2] not in {"!", "^"} else index + 3
        if close < minimum:
            raise TaskRunError(f"scope glob has an invalid character class: {scope!r}")
        index = close + 1


def _glob_matches(root: Path, pattern: str) -> tuple[list[str], list[str]]:
    root = root.resolve()
    matches: list[str] = []
    directories: list[str] = []
    for candidate in root.glob(pattern):
        resolved = candidate.resolve()
        if not _is_inside(resolved, root):
            raise TaskRunError(
                f"scope glob resolved outside the repository: {pattern!r} -> {candidate}"
            )
        relative = candidate.relative_to(root).as_posix()
        matches.append(relative)
        if candidate.is_dir():
            directories.append(relative)
    return sorted(set(matches)), sorted(set(directories))


def resolve_scope_specs(root: Path, scopes: Sequence[str]) -> list[dict[str, Any]]:
    """Freeze literal semantics and expand each glob before worktree creation."""
    specs: list[dict[str, Any]] = []
    for scope in scopes:
        if not _is_glob_scope(scope):
            specs.append(
                {"path": scope, "kind": "directory" if (root / scope).is_dir() else "exact"}
            )
            continue
        _validate_glob_scope(scope)
        matches, directories = _glob_matches(root, scope)
        if not matches:
            raise TaskRunError(f"scope glob matched no paths: {scope!r}")
        specs.append(
            {
                "path": scope,
                "kind": "glob",
                "matches": matches,
                "match_count": len(matches),
                "directory_matches": directories,
            }
        )
    return specs


def _refresh_scope_specs(
    root: Path, specs: Sequence[Mapping[str, Any]]
) -> list[dict[str, Any]]:
    refreshed: list[dict[str, Any]] = []
    for source in specs:
        spec = dict(source)
        if spec["kind"] == "glob":
            current, current_directories = _glob_matches(root, str(spec["path"]))
            matches = sorted(set(spec.get("matches", ())) | set(current))
            directories = sorted(
                set(spec.get("directory_matches", ())) | set(current_directories)
            )
            spec.update(
                matches=matches,
                match_count=len(matches),
                directory_matches=directories,
            )
        refreshed.append(spec)
    return refreshed


def _scope_matches(path: str, spec: Mapping[str, Any]) -> bool:
    scope = spec["path"]
    if spec["kind"] == "glob":
        return path in spec.get("matches", ()) or any(
            path.startswith(directory.rstrip("/") + "/")
            for directory in spec.get("directory_matches", ())
        )
    return path == scope or (
        spec["kind"] == "directory" and path.startswith(scope.rstrip("/") + "/")
    )


def _paths_in_scopes(paths: Sequence[str], specs: Sequence[Mapping[str, Any]]) -> list[str]:
    return sorted(path for path in paths if any(_scope_matches(path, spec) for spec in specs))


def _scope_result(
    repo_root: Path,
    base_sha: str,
    specs: Sequence[Mapping[str, Any]],
    require_change: bool,
) -> dict[str, Any]:
    changed = _changed_paths(repo_root, base_sha)
    allowed = _paths_in_scopes(changed, specs)
    disallowed = sorted(set(changed) - set(allowed))
    if disallowed:
        verdict, reason = FAIL, "candidate changes paths outside the declared scope"
    elif require_change and not changed:
        verdict, reason = FAIL, "the task required a change but the worktree is unchanged"
    else:
        verdict, reason = PASS, "all candidate changes are within the declared scope"
    return {
        "verdict": verdict,
        "reason": reason,
        "specs": [dict(spec) for spec in specs],
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
    populations: Mapping[str, Any],
    specs: Sequence[Mapping[str, Any]],
) -> list[dict[str, str]]:
    generated: list[dict[str, str]] = []
    for population in ("untracked", "ignored"):
        for path in populations[population].get("added", []):
            candidate = population == "untracked" and any(
                _scope_matches(path, spec) for spec in specs
            )
            generated.append(
                {
                    "population": population,
                    "path": path,
                    "classification": "candidate" if candidate else "diagnostic",
                    "cause": (
                        "new candidate path is within the declared scope"
                        if candidate
                        else _path_cause(path)
                    ),
                }
            )
    return generated


_TASK_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,95}$")


def validate_lane_id(lane: str) -> str:
    """Validate the safe identifier used by the shorthand lane mode."""
    value = lane.strip()
    if not _TASK_ID_RE.fullmatch(value):
        raise TaskRunError(
            "--lane must be a non-empty id starting with a letter or digit and "
            "containing only letters, digits, dot, underscore, or dash (maximum 96 characters)"
        )
    return value


def _task_id(branch: str, requested: str | None) -> str:
    if requested is not None:
        task_id = requested.strip()
        if not _TASK_ID_RE.fullmatch(task_id):
            raise TaskRunError(
                "--task-id must start with a letter or digit and contain only letters, "
                "digits, dot, underscore, or dash (maximum 96 characters)"
            )
        return task_id
    generated = re.sub(r"[^A-Za-z0-9._-]+", "-", branch.replace("/", "-")).strip("-")[:96]
    return generated or "task"


def build_codex_args(
    *,
    effort: str | None = None,
    writable_dirs: Sequence[Path] = (),
    extra: Sequence[str] = (),
) -> list[str]:
    """Build Codex host arguments with the task runner's fixed Luna model."""
    for index, value in enumerate(extra):
        if value in {"-m", "--model"} or value.startswith(("-m=", "--model=")):
            raise TaskRunError("charness task fixes the Codex model to gpt-5.6-luna")
        if re.match(r"^(?:-c|--config)=?\s*model\s*=", value) or (
            index > 0
            and extra[index - 1] in {"-c", "--config"}
            and re.match(r"^\s*model\s*=", value)
        ):
            raise TaskRunError("charness task fixes the Codex model to gpt-5.6-luna")
    args: list[str] = ["--sandbox", "workspace-write"]
    for writable_dir in writable_dirs:
        args.extend(["--add-dir", str(writable_dir.resolve())])
    args.extend(extra)
    args.extend(["-m", TASK_MODEL])
    if effort is not None:
        if effort not in TASK_EFFORTS:
            allowed = ", ".join(TASK_EFFORTS)
            raise TaskRunError(f"--effort must be one of: {allowed}")
        args.extend(["-c", f"model_reasoning_effort={effort}"])
    return args


def build_codex_command(
    executable: str,
    prompt: str,
    *,
    effort: str | None = None,
    writable_dirs: Sequence[Path] = (),
    extra: Sequence[str] = (),
) -> list[str]:
    """Build the one Codex command used by previews and real task runs."""
    return [
        executable,
        "exec",
        *build_codex_args(
            effort=effort,
            writable_dirs=writable_dirs,
            extra=extra,
        ),
        prompt,
    ]


def task_runtime_root(repo_root: Path) -> Path:
    """Resolve the task result store by clean parent identity, ignoring ambient roots."""
    preview_env = os.environ.copy()
    for key in ("CHARNESS_RUNTIME_ROOT", "CHARNESS_RUNTIME_ROOT_AUTO", "CHARNESS_RUNTIME_REPO_KEY"):
        preview_env.pop(key, None)
    return runtime_root(repo_root, preview_env)


def task_result_path(runtime_path: Path, task_id: str) -> Path:
    if not _TASK_ID_RE.fullmatch(task_id):
        raise TaskRunError(f"invalid task id: {task_id!r}")
    return runtime_path / "task-run" / task_id / "result.json"


def write_task_result(runtime_path: Path, result: Mapping[str, Any]) -> Path:
    """Atomically publish the sole persisted task-run result."""
    path = task_result_path(runtime_path, str(result["task_id"]))
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=".result.", suffix=".tmp", dir=path.parent)
    temp_path = Path(temp_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(dict(result), handle, ensure_ascii=False, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_path, path)
    finally:
        temp_path.unlink(missing_ok=True)
    return path


def read_task_result(runtime_path: Path, task_id: str) -> dict[str, Any] | None:
    path = task_result_path(runtime_path, task_id)
    if not path.is_file():
        return None
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise TaskRunError(f"task result must be a JSON object: {path}")
    return payload


def read_task_results(runtime_path: Path) -> list[dict[str, Any]]:
    root = runtime_path / "task-run"
    results: list[dict[str, Any]] = []
    for path in sorted(root.glob("*/result.json")) if root.is_dir() else []:
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise TaskRunError(f"task result must be a JSON object: {path}")
        results.append(payload)
    return results


def _failure_payload(
    *,
    repo_root: Path | None,
    target_path: Path | None,
    task_id: str | None,
    error: str,
) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "event": "task-run",
        "status": FAIL,
        "phase": "preflight",
        "approval_eligibility": "ineligible",
        "repo_root": str(repo_root) if repo_root is not None else None,
        "worktree_path": str(target_path) if target_path is not None else None,
        "task_id": task_id,
        "error": error,
        "next_step": "Fix the preflight error, then rerun task run from a clean parent with an unused worktree path.",
    }


def _runtime_preview(repo_root: Path) -> Path:
    return task_runtime_root(repo_root)


def _execute_codex(
    command: Sequence[str],
    *,
    target_path: Path,
    configured_env: Mapping[str, str],
    stdout_log: Path,
    stderr_log: Path,
    timeout_seconds: int,
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "exit_code": None,
        "timed_out": False,
        "interrupted": False,
    }
    try:
        with (
            stdout_log.open("w", encoding="utf-8") as stdout_handle,
            stderr_log.open("w", encoding="utf-8") as stderr_handle,
        ):
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
    except KeyboardInterrupt:
        result["interrupted"] = True
    except OSError as exc:
        result["exec_error"] = str(exc)
    return result


_MAX_RESULT_TEXT_BYTES = 1024 * 1024


def _result_delivery(stdout_log: Path) -> dict[str, Any]:
    raw = stdout_log.read_bytes() if stdout_log.is_file() else b""
    delivered = bool(raw.strip())
    clipped = raw[:_MAX_RESULT_TEXT_BYTES]
    text = clipped.decode("utf-8", errors="replace")
    result: dict[str, Any] = {
        "status": "delivered" if delivered else "non-delivery",
        "bytes": len(raw),
        "truncated": len(raw) > len(clipped),
        "text": text,
        "log": str(stdout_log),
    }
    result["structured_status"] = "not-applicable"
    if delivered and not result["truncated"]:
        try:
            structured = yaml.safe_load(text)
        except yaml.YAMLError:
            if "schema_version" in text:
                result["structured_status"] = "invalid"
        else:
            if isinstance(structured, Mapping) and "schema_version" in structured:
                result["structured_status"] = "valid"
                result["structured"] = dict(structured)
    return result


def _parent_progress(
    *,
    parent_root: Path,
    parent_before: Mapping[str, Sequence[str]],
    parent_before_head: str,
    specs: Sequence[Mapping[str, Any]],
) -> tuple[dict[str, Any], dict[str, list[str]]]:
    parent_after = _collect_populations(parent_root)
    parent_after_head = _git_output(parent_root, "rev-parse", "HEAD").strip()
    committed = (
        _parse_nul_paths(
            _git_output(
                parent_root,
                "diff",
                "--no-renames",
                "--name-only",
                "-z",
                parent_before_head,
                parent_after_head,
                "--",
            )
        )
        if parent_before_head != parent_after_head
        else []
    )
    dirty_paths: list[str] = []
    dirty_delta: dict[str, dict[str, list[str]]] = {}
    for population in ("tracked", "untracked"):
        before = set(parent_before.get(population, ()))
        after = set(parent_after.get(population, ()))
        added = sorted(after - before)
        removed = sorted(before - after)
        dirty_delta[population] = {"added": added, "removed": removed}
        dirty_paths.extend(added)
        dirty_paths.extend(removed)

    ignored_before = set(parent_before.get("ignored", ()))
    ignored_after = set(parent_after.get("ignored", ()))
    ignored_delta = {
        "added": sorted(ignored_after - ignored_before),
        "removed": sorted(ignored_before - ignored_after),
        "paths": sorted(ignored_after),
    }
    changed = sorted(set(committed) | set(dirty_paths))
    overlap = _paths_in_scopes(changed, _refresh_scope_specs(parent_root, specs))
    classification = (
        "normal"
        if not changed
        else "writer-conflict"
        if overlap
        else "concurrent-parent-progress"
    )
    progress = {
        "classification": classification,
        "blocking": classification == "writer-conflict",
        "committed_paths": committed,
        "dirty": dirty_delta,
        "paths": changed,
        "overlap_paths": overlap,
        "ignored": ignored_delta,
        "before_head": parent_before_head,
        "after_head": parent_after_head,
    }
    return progress, parent_after


def _completion_evidence(
    *,
    target_path: Path,
    parent_root: Path,
    before_exec: Mapping[str, Sequence[str]],
    base_sha: str,
    scope_specs: Sequence[Mapping[str, Any]],
    require_change: bool,
    parent_before: Mapping[str, Sequence[str]],
    parent_before_head: str,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    after_exec = _collect_populations(target_path)
    populations = _population_delta(before_exec, after_exec)
    target_scope_specs = _refresh_scope_specs(target_path, scope_specs)
    scope = _scope_result(target_path, base_sha, target_scope_specs, require_change)
    parent_progress, parent_after = _parent_progress(
        parent_root=parent_root,
        parent_before=parent_before,
        parent_before_head=parent_before_head,
        specs=scope_specs,
    )
    evidence = {
        "after_exec": _snapshot_payload(after_exec),
        "populations": populations,
        "generated_files": _generated_files(populations, target_scope_specs),
        "scope": scope,
        "parent": {
            "unchanged": parent_progress["classification"] == "normal",
            "before": _snapshot_payload(parent_before),
            "after": _snapshot_payload(parent_after),
            "progress": parent_progress,
            "verdict": FAIL if parent_progress["blocking"] else PASS,
        },
    }
    return evidence, scope, parent_progress
