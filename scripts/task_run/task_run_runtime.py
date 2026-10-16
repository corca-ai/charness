"""Task identity, Codex command construction, and result-store persistence."""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import stat
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence


def _load_repo_runtime_bootstrap():
    pathlib, sys = __import__("pathlib"), __import__("sys")
    marker = ("scripts", "adapter_lib.py")
    parents = pathlib.Path(__file__).resolve().parents
    root = next((p for p in parents if p.joinpath(*marker).is_file()), None)
    if root is not None and str(root) not in sys.path:
        sys.path.insert(0, str(root))


_load_repo_runtime_bootstrap()

from scripts.runtime_bootstrap import runtime_root  # noqa: E402
from scripts.task_run import task_run_git as _git_owner  # noqa: E402
from scripts.task_run.task_run_contract import (  # noqa: E402
    _TASK_ID_RE,
    FAIL,
    SCHEMA_VERSION,
    TASK_EFFORTS,
    TASK_MODEL,
    TASK_MUSE_EFFORTS,
    TaskRunError,
)


def _resolve_lane_executable(
    value: str, *, empty_error: str, not_runnable: str, not_on_path: str
) -> str:
    """The one executable-resolution core; wrappers only name their executor."""
    if not value.strip():
        raise TaskRunError(empty_error)
    if "/" in value:
        candidate = Path(value).expanduser().resolve()
        if not candidate.is_file() or not os.access(candidate, os.X_OK):
            raise TaskRunError(f"{not_runnable}: {value}")
        return str(candidate)
    resolved = shutil.which(value)
    if resolved is None:
        raise TaskRunError(f"{not_on_path}: {value}")
    return resolved


def _resolve_codex(value: str) -> str:
    return _resolve_lane_executable(
        value,
        empty_error="--codex must name an executable",
        not_runnable="Codex executable is not runnable",
        not_on_path="Codex executable is not on PATH",
    )


def resolve_executor_executable(value: str, *, executor: str) -> str:
    """Resolve the lane executable for the selected executor."""
    return _resolve_lane_executable(
        value,
        empty_error=f"{executor} executor must name an executable",
        not_runnable=f"{executor} executable is not runnable",
        not_on_path=f"{executor} executable is not on PATH",
    )


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
        raise TaskRunError(f"--effort must be one of: {allowed} (codex executor)")
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


def build_muse_args(
    *,
    effort: str,
    prompt_file: Path,
    worktree: Path,
) -> list[str]:
    """Build Muse host arguments with the task runner's curated effort preset.

    `muse exec` takes no stdin prompt, so the lane prompt travels via
    `--prompt-file`. Approval prompts cannot be answered headless, so they are
    disabled; the OS sandbox stays on (the Codex lane's workspace-write
    equivalent). `muse exec` honors a single effective workspace (the last
    `--workspace` wins), so the lane worktree root is passed exactly once:
    passing every writable dir rooted the lane at `<worktree>/.agents` and
    every write outside it was refused (#814). The lane worktree is created
    for the agent, so it is trusted: otherwise the repo's rules are skipped
    and delegation stays unavailable. `--json` streams machine-readable
    events on stdout: without it the lane stdout stays empty until the run
    ends, so a timed-out lane receipted no phases and no retry cause (#886).
    The terminal report is extracted from the `run_terminal` event, separate
    from that JSONL transport.
    """
    if effort not in TASK_MUSE_EFFORTS:
        allowed = ", ".join(TASK_MUSE_EFFORTS)
        raise TaskRunError(f"--effort must be one of: {allowed} (muse executor)")
    return [
        "--json",
        "--reasoning-effort",
        effort,
        "--disable-approval",
        "--trust-workspace",
        "--workspace",
        str(worktree),
        "--prompt-file",
        str(prompt_file),
    ]


def build_muse_command(
    executable: str,
    *,
    effort: str,
    prompt_file: Path,
    worktree: Path,
) -> list[str]:
    """Build the Muse command; the task prompt travels via --prompt-file."""
    return [
        executable,
        "exec",
        *build_muse_args(
            effort=effort, prompt_file=prompt_file, worktree=worktree
        ),
    ]


#: Env-name fragments (case-insensitive) treated as secret-bearing (#832).
#: The lane child inherits ambient env, and an executor may re-emit its
#: environment where any local process can read it (observed: muse
#: `--env-json` argv). Names only are ever matched or recorded, never values.
_SECRET_ENV_FRAGMENTS = (
    "API_KEY",
    "APIKEY",
    "_TOKEN",
    "TOKEN_",
    "SECRET",
    "PASSWD",
    "PASSWORD",
    "PRIVATE_KEY",
    "CREDENTIALS",
    "ACCESS_TOKEN",
    "AUTH_TOKEN",
    "REFRESH_TOKEN",
    "SESSION_TOKEN",
    "CLIENT_SECRET",
)
_SECRET_ENV_EXACT = frozenset({"TOKEN", "API_KEY", "SECRET", "PASSWORD"})

#: Executor auth keys that must stay in the lane env to function (#832).
#: Muse authenticates from its stored credentials; codex reads its key here.
_EXECUTOR_SECRET_KEEPS: dict[str, frozenset[str]] = {
    "codex": frozenset({"OPENAI_API_KEY"}),
    "muse": frozenset(),
}

#: Operator override: comma-separated exact env names to keep in lane env.
LANE_KEEP_SECRET_ENV = "CHARNESS_TASK_RUN_KEEP_SECRET_ENV"


def _is_secret_env_name(name: str) -> bool:
    upper = name.upper()
    return upper in _SECRET_ENV_EXACT or any(
        fragment in upper for fragment in _SECRET_ENV_FRAGMENTS
    )


def scrubbed_lane_env(
    payload: dict[str, Any],
    env: Mapping[str, str],
    executor: str,
) -> dict[str, str]:
    """Drop secret-pattern names from the lane child env, recording names (#832).

    Unknown executors keep nothing secret-patterned (fail closed). Only the
    executor's auth keeps and explicit `CHARNESS_TASK_RUN_KEEP_SECRET_ENV`
    names survive; the receipt records scrubbed/kept names, never values.
    """
    keeps = set(_EXECUTOR_SECRET_KEEPS.get(executor, frozenset()))
    for extra in os.environ.get(LANE_KEEP_SECRET_ENV, "").split(","):
        if extra.strip():
            keeps.add(extra.strip())
    scrubbed = sorted(
        name for name in env if _is_secret_env_name(name) and name not in keeps
    )
    kept = sorted(
        name for name in env if _is_secret_env_name(name) and name in keeps
    )
    payload["lane_env"] = {
        "executor": executor,
        "scrubbed": scrubbed,
        "kept_secret_names": kept,
    }
    return {name: value for name, value in env.items() if name not in scrubbed}


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


def utc_now_iso() -> str:
    """Wall-clock stamp for the receipt; the runtime's own clock, never a test's."""
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def runner_liveness(record: Mapping[str, Any]) -> dict[str, Any]:
    """Advisory pid check on the runner that wrote this record.

    A lane's record read `timed-out` while its runner was visibly alive (#791),
    and the record could not say which reading was stale because it carried no
    process identity. `alive` is `os.kill(pid, 0)` at read time, never
    persisted, and only advisory: a pid can be reused, and a live runner on a
    terminal record is normal while the runner finishes retention after its
    final write. A `running` record whose pid is dead is the one firm reading:
    that record is stale.
    """
    pid = record.get("runner_pid")
    if not isinstance(pid, int) or pid <= 0:
        return {"runner_pid": None, "alive": None}
    try:
        os.kill(pid, 0)
        alive = True
    except ProcessLookupError:
        alive = False
    except PermissionError:
        alive = True
    return {"runner_pid": pid, "alive": alive}


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


#: Aggregate inventory event, beside `task-status` and `task-status-list`.
INVENTORY_EVENT = "task-status-inventory"
#: The inventory covers this repo's managed runtime tree, never the machine.
MANAGED_TREE_SCOPE = "managed-runtime-tree"
#: An explicit standalone runtime root has no sibling keys; the inventory says so.
SINGLE_ROOT_SCOPE = "single-runtime-root"

#: Typed unknown causes. An admission consumer must never read a partial
#: inventory as zero capacity use, so every unclassifiable record carries one.
UNKNOWN_UNREADABLE = "unreadable-result"
UNKNOWN_MALFORMED = "malformed-result"
UNKNOWN_RUNNER_UNCONFIRMED = "runner-unconfirmed"
UNKNOWN_RECORD_MISSING = "record-missing"
UNKNOWN_STATUS = "unknown-status"


def _compact_inventory_entry(
    *,
    task_id: str,
    repo_root: str | None,
    runtime_root: Path,
    result_path: Path,
    status: str,
    phase: str,
    liveness: dict[str, Any],
    inventory_state: str,
    reason_code: str | None,
) -> dict[str, Any]:
    """One bounded entry: identity/repo/runtime/phase/liveness, never the record."""
    return {
        "task_id": task_id,
        "repo_root": repo_root,
        "runtime_root": str(runtime_root),
        "result_path": str(result_path),
        "status": status,
        "phase": phase,
        "liveness": liveness,
        "inventory_state": inventory_state,
        "reason_code": reason_code,
    }


def _unknown_inventory_entry(
    *,
    task_id: str,
    runtime_root: Path,
    result_path: Path,
    reason_code: str,
) -> dict[str, Any]:
    return _compact_inventory_entry(
        task_id=task_id,
        repo_root=None,
        runtime_root=runtime_root,
        result_path=result_path,
        status="unknown",
        phase="unknown",
        liveness={"runner_pid": None, "alive": None},
        inventory_state="unknown",
        reason_code=reason_code,
    )


def inventory_entry_for_result(result_path: Path, runtime_root: Path) -> dict[str, Any]:
    """Classify one persisted result with canonical `runner_liveness` semantics.

    Read-only: the result file is never repaired or rewritten. Only a `running`
    record with a live runner counts as `running`; a terminal record with a
    live runner is normal retention (`terminal`); a `running` record with a dead
    runner is `stale`. Anything unclassifiable is `unknown` with a typed
    `reason_code`, so a partial inventory can never read as zero capacity use.
    """
    fallback_id = result_path.parent.name
    try:
        text = result_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return _unknown_inventory_entry(
            task_id=fallback_id,
            runtime_root=runtime_root,
            result_path=result_path,
            reason_code=UNKNOWN_RECORD_MISSING,
        )
    except OSError:
        return _unknown_inventory_entry(
            task_id=fallback_id,
            runtime_root=runtime_root,
            result_path=result_path,
            reason_code=UNKNOWN_UNREADABLE,
        )
    try:
        payload = json.loads(text)
    except ValueError:
        return _unknown_inventory_entry(
            task_id=fallback_id,
            runtime_root=runtime_root,
            result_path=result_path,
            reason_code=UNKNOWN_MALFORMED,
        )
    if not isinstance(payload, dict):
        return _unknown_inventory_entry(
            task_id=fallback_id,
            runtime_root=runtime_root,
            result_path=result_path,
            reason_code=UNKNOWN_MALFORMED,
        )
    raw_task_id = payload.get("task_id")
    task_id = raw_task_id if isinstance(raw_task_id, str) and raw_task_id else fallback_id
    status = payload.get("status")
    phase = payload.get("phase")
    if not isinstance(status, str) or not status:
        return _unknown_inventory_entry(
            task_id=task_id,
            runtime_root=runtime_root,
            result_path=result_path,
            reason_code=UNKNOWN_MALFORMED,
        )
    phase_text = phase if isinstance(phase, str) and phase else "unknown"
    liveness = runner_liveness(payload)
    raw_repo = payload.get("repo_root")
    repo_text = raw_repo if isinstance(raw_repo, str) and raw_repo else None
    if status == "running":
        if liveness.get("alive") is True:
            state: str = "running"
            reason: str | None = None
        elif liveness.get("alive") is False:
            state = "stale"
            reason = None
        else:
            state = "unknown"
            reason = UNKNOWN_RUNNER_UNCONFIRMED
    else:
        from scripts.task_run.task_run_state import is_known_terminal_status

        if not is_known_terminal_status(status):
            return _compact_inventory_entry(
                task_id=task_id,
                repo_root=repo_text,
                runtime_root=runtime_root,
                result_path=result_path,
                status=status,
                phase=phase_text,
                liveness=liveness,
                inventory_state="unknown",
                reason_code=UNKNOWN_STATUS,
            )
        return _compact_inventory_entry(
            task_id=task_id,
            repo_root=repo_text,
            runtime_root=runtime_root,
            result_path=result_path,
            status=status,
            phase=phase_text,
            liveness=liveness,
            inventory_state="terminal",
            reason_code=None,
        )
    return _compact_inventory_entry(
        task_id=task_id,
        repo_root=repo_text,
        runtime_root=runtime_root,
        result_path=result_path,
        status=status,
        phase=phase_text,
        liveness=liveness,
        inventory_state=state,
        reason_code=reason,
    )


def _result_in_task_dir(
    task_dir: os.DirEntry[str], key_root: Path
) -> tuple[Path | None, dict[str, Any] | None]:
    """Check only the exact canonical result path without following symlinks."""
    result_path = Path(task_dir.path) / "result.json"
    try:
        result_stat = result_path.lstat()
    except FileNotFoundError:
        return None, None
    except OSError:
        return None, _unknown_inventory_entry(
            task_id=task_dir.name,
            runtime_root=key_root,
            result_path=result_path,
            reason_code=UNKNOWN_UNREADABLE,
        )
    if stat.S_ISREG(result_stat.st_mode):
        return result_path, None
    return None, _unknown_inventory_entry(
        task_id=task_dir.name,
        runtime_root=key_root,
        result_path=result_path,
        reason_code=UNKNOWN_UNREADABLE,
    )


def _enumerate_task_results(
    key_root: Path,
) -> tuple[list[Path], list[dict[str, Any]], list[str]]:
    """Enumerate immediate task result files without following symlinks."""
    store = key_root / "task-run"
    results: list[Path] = []
    unknown: list[dict[str, Any]] = []
    reasons: list[str] = []
    try:
        store_stat = store.lstat()
    except FileNotFoundError:
        return results, unknown, reasons
    except OSError as exc:
        return results, unknown, [f"unreadable task-run store under {key_root}: {exc}"]
    if not stat.S_ISDIR(store_stat.st_mode):
        return results, unknown, reasons

    try:
        with os.scandir(store) as task_dirs:
            for task_dir in task_dirs:
                try:
                    task_dir_stat = task_dir.stat(follow_symlinks=False)
                except FileNotFoundError:
                    continue
                except OSError as exc:
                    reasons.append(
                        f"unreadable task-run entry under {key_root}: {exc}"
                    )
                    continue
                if not stat.S_ISDIR(task_dir_stat.st_mode):
                    continue
                result_path, unknown_entry = _result_in_task_dir(task_dir, key_root)
                if result_path is not None:
                    results.append(result_path)
                if unknown_entry is not None:
                    unknown.append(unknown_entry)
    except OSError as exc:
        reasons.append(f"unreadable task-run store under {key_root}: {exc}")
    return results, unknown, reasons


def _inventory_for_key(
    key_root: Path,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], int, list[str]]:
    """Classify one key's top-level `task-run` store; never recurse.

    Only immediate `<key>/task-run/*/result.json` records are read: nested keys
    under `xdg-cache` and lane-private `runtime/` dirs are not stores, so one
    task is never double-counted. Returns
    (running, stale, unknown, terminal_count, completeness_reasons); terminal
    lanes contribute a count only, since that list can be huge.
    """
    running: list[dict[str, Any]] = []
    stale: list[dict[str, Any]] = []
    results, unknown, reasons = _enumerate_task_results(key_root)
    terminal_count = 0
    for result_path in sorted(results):
        entry = inventory_entry_for_result(result_path, key_root)
        state = entry["inventory_state"]
        if state == "running":
            running.append(entry)
        elif state == "stale":
            stale.append(entry)
        elif state == "unknown":
            unknown.append(entry)
        else:
            terminal_count += 1
    return running, stale, unknown, terminal_count, reasons


def _inventory_counts(
    running: list[dict[str, Any]],
    stale: list[dict[str, Any]],
    unknown: list[dict[str, Any]],
    terminal_count: int,
    completeness_reasons: list[str],
) -> dict[str, Any]:
    """Build the compact shared counts and completeness portion of inventory."""
    reasons = list(completeness_reasons)
    if unknown:
        reasons.append(
            f"{len(unknown)} task record(s) could not be classified; see unknown_reasons"
        )
    running.sort(key=lambda entry: (entry["task_id"], entry["runtime_root"]))
    unknown_reasons: dict[str, int] = {}
    for entry in unknown:
        reason = entry["reason_code"]
        unknown_reasons[reason] = unknown_reasons.get(reason, 0) + 1
    return {
        "running_count": len(running),
        "stale_count": len(stale),
        "terminal_count": terminal_count,
        "unknown_count": len(unknown),
        "completeness": "partial" if (unknown or reasons) else "complete",
        "completeness_reasons": reasons,
        "running_tasks": running,
        "unknown_reasons": unknown_reasons,
    }


def running_inventory_for_keys_root(keys_root: Path) -> dict[str, Any]:
    """Compact canonical running-task inventory across one managed runtime tree.

    Pure enumeration plus the canonical `runner_liveness` check: no Git repos,
    commits, spawns, or sleeps, and no mutation of any result file. The boundary
    is the caller-supplied `<base>/charness/runtime` tree; only its immediate
    keys are read, so sandbox fixtures elsewhere are never part of the claim.
    """
    keys_root = keys_root.expanduser().resolve()
    running: list[dict[str, Any]] = []
    stale: list[dict[str, Any]] = []
    unknown: list[dict[str, Any]] = []
    terminal_count = 0
    completeness_reasons: list[str] = []
    try:
        children = sorted(keys_root.iterdir())
    except OSError as exc:
        return {
            "schema_version": SCHEMA_VERSION,
            "event": INVENTORY_EVENT,
            "keys_root": str(keys_root),
            "scope": MANAGED_TREE_SCOPE,
            "machine_global": False,
            "running_count": 0,
            "stale_count": 0,
            "terminal_count": 0,
            "unknown_count": 0,
            "completeness": "partial",
            "completeness_reasons": [f"unreadable keys root {keys_root}: {exc}"],
            "running_tasks": [],
            "unknown_reasons": {"unreadable-keys-root": 1},
        }
    for key in children:
        if key.is_symlink() or not key.is_dir():
            continue
        key_running, key_stale, key_unknown, key_terminal, reasons = _inventory_for_key(key)
        running.extend(key_running)
        stale.extend(key_stale)
        unknown.extend(key_unknown)
        terminal_count += key_terminal
        completeness_reasons.extend(reasons)
    return {
        "schema_version": SCHEMA_VERSION,
        "event": INVENTORY_EVENT,
        "keys_root": str(keys_root),
        "scope": MANAGED_TREE_SCOPE,
        "machine_global": False,
        **_inventory_counts(
            running, stale, unknown, terminal_count, completeness_reasons
        ),
    }


def task_running_inventory(repo_root: Path) -> dict[str, Any]:
    """Aggregate inventory for this repo's managed runtime tree, read-only.

    The tree boundary comes from the existing runtime owner: this repo's key
    under `<base>/charness/runtime` (`scripts/runtime_bootstrap.py`,
    `keys_root_of` in `scripts/gates_support/runtime_root_retention.py`). A
    custom standalone runtime root has no sibling keys, so the inventory
    honestly narrows to that single root with its limitation stated instead of
    an unprovable machine-global claim.
    """
    from scripts.gates_support.runtime_root_retention import keys_root_of  # noqa: E402

    resolved_repo = _git_owner._require_git_root(repo_root)
    runtime_path = task_runtime_root(resolved_repo)
    try:
        keys_root = keys_root_of(runtime_path.resolve())
    except ValueError:
        running, stale, unknown, terminal_count, reasons = _inventory_for_key(runtime_path)
        return {
            "schema_version": SCHEMA_VERSION,
            "event": INVENTORY_EVENT,
            "repo_root": str(resolved_repo),
            "runtime_root": str(runtime_path),
            "keys_root": None,
            "scope": SINGLE_ROOT_SCOPE,
            "scope_limitation": (
                "explicit CHARNESS_RUNTIME_ROOT is not a charness runtime key, "
                "so it has no sibling keys; this inventory covers only that "
                "single runtime root, never the managed tree and never the machine"
            ),
            "machine_global": False,
            **_inventory_counts(running, stale, unknown, terminal_count, reasons),
        }
    payload = running_inventory_for_keys_root(keys_root)
    payload["repo_root"] = str(resolved_repo)
    payload["runtime_root"] = str(runtime_path)
    return payload


def task_status(
    repo_root: Path, task_id: str | None = None, *, all_repos: bool = False
) -> dict[str, Any]:
    """Read the one external task-run result store without mutation."""
    if all_repos:
        if task_id is not None:
            raise TaskRunError("--all-repos cannot be combined with a task id")
        return task_running_inventory(repo_root)
    resolved_repo = _git_owner._require_git_root(repo_root)
    runtime_path = task_runtime_root(resolved_repo)
    if task_id is not None:
        record = read_task_result(runtime_path, task_id)
        if record is not None:
            return {**record, "liveness": runner_liveness(record)}
        return {
            "schema_version": SCHEMA_VERSION,
            "event": "task-status",
            "repo_root": str(resolved_repo),
            "task_id": task_id,
            "status": "missing",
            "result_path": str(task_result_path(runtime_path, task_id)),
        }
    return {
        "schema_version": SCHEMA_VERSION,
        "event": "task-status-list",
        "repo_root": str(resolved_repo),
        "runtime_root": str(runtime_path),
        "tasks": [
            {**record, "liveness": runner_liveness(record)}
            for record in read_task_results(runtime_path)
        ],
    }


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
