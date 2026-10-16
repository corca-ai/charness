"""Canonical task status read model and aggregate runtime inventory."""

from __future__ import annotations

import json
import os
import stat
from pathlib import Path
from typing import Any

from scripts.task_run import task_run_git as _git_owner
from scripts.task_run import task_run_runtime as _runtime
from scripts.task_run.task_run_contract import (  # noqa: E402
    SCHEMA_VERSION,
    TaskRunError,
)

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
    liveness = _runtime.runner_liveness(payload)
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
        return results, unknown, [
            f"task-run store under {key_root} is not a directory"
        ]

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
    runtime_path = _runtime.task_runtime_root(resolved_repo)
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
    """Dispatch status reads to the per-runtime or aggregate inventory owner."""
    if all_repos:
        if task_id is not None:
            raise TaskRunError("--all-repos cannot be combined with a task id")
        return task_running_inventory(repo_root)
    return _runtime.task_status(repo_root, task_id)
