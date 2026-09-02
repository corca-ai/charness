"""Task identity, Codex command construction, and result-store persistence."""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import tempfile
from pathlib import Path
from typing import Any, Mapping, Sequence


def _load_repo_runtime_bootstrap():
    _repo_bootstrap_pathlib = __import__("pathlib")
    _repo_bootstrap_sys = __import__("sys")
    repo_root = next(
        (
            ancestor
            for ancestor in _repo_bootstrap_pathlib.Path(__file__).resolve().parents
            if (ancestor / "scripts" / "adapter_lib.py").is_file()
        ),
        None,
    )
    if repo_root is None:
        raise ImportError("scripts/adapter_lib.py not found")
    repo_root_text = str(repo_root)
    if repo_root_text not in _repo_bootstrap_sys.path:
        _repo_bootstrap_sys.path.insert(0, repo_root_text)


_load_repo_runtime_bootstrap()

from scripts.runtime_bootstrap import runtime_root  # noqa: E402
from scripts.task_run_contract import (  # noqa: E402
    _TASK_ID_RE,
    FAIL,
    SCHEMA_VERSION,
    TASK_EFFORTS,
    TASK_MODEL,
    TaskRunError,
)


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


def validate_lane_id(lane: str) -> str:
    """Validate the safe identifier used by shorthand lane mode."""
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
    slug = re.sub(r"[^A-Za-z0-9._-]+", "-", branch.replace("/", "-")).strip("-")
    digest = hashlib.sha256(branch.encode("utf-8")).hexdigest()[:8]
    return f"{slug[:87] or 'task'}-{digest}"


def build_codex_args(
    *,
    effort: str,
    writable_dirs: Sequence[Path] = (),
) -> list[str]:
    """Build Codex host arguments with the task runner's fixed Luna model."""
    args: list[str] = ["--sandbox", "workspace-write"]
    for writable_dir in writable_dirs:
        args.extend(["--add-dir", str(writable_dir.resolve())])
    args.extend(["-m", TASK_MODEL])
    if effort not in TASK_EFFORTS:
        allowed = ", ".join(TASK_EFFORTS)
        raise TaskRunError(f"--effort must be one of: {allowed}")
    args.extend(["-c", f"model_reasoning_effort={effort}"])
    return args


def build_codex_command(
    executable: str,
    *,
    effort: str,
    writable_dirs: Sequence[Path] = (),
) -> list[str]:
    """Build the Codex command; the task prompt is supplied on stdin."""
    return [
        executable,
        "exec",
        *build_codex_args(effort=effort, writable_dirs=writable_dirs),
        "-",
    ]


def task_runtime_root(repo_root: Path) -> Path:
    """Resolve the result store by clean parent identity, ignoring ambient roots."""
    preview_env = os.environ.copy()
    for key in ("CHARNESS_RUNTIME_ROOT", "CHARNESS_RUNTIME_ROOT_AUTO", "CHARNESS_RUNTIME_REPO_KEY"):
        preview_env.pop(key, None)
    return runtime_root(repo_root, preview_env)


def task_result_path(runtime_path: Path, task_id: str) -> Path:
    if not _TASK_ID_RE.fullmatch(task_id):
        raise TaskRunError(f"invalid task id: {task_id!r}")
    return runtime_path / "task-run" / task_id / "result.json"


def task_execution_runtime_root(runtime_path: Path, task_id: str) -> Path:
    """Return the lane-private runtime root beneath one task result directory."""
    return task_result_path(runtime_path, task_id).parent / "runtime"


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
