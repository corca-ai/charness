"""Pure readers of a lane's signals: phase markers, the blocker line, the first-edit stall.

Split from `task_run_progress` (the live watch) so the watch module holds the
polling loop and its actions, and these readers stay testable on their own.
`task_run_progress` re-exports every name here for its existing callers.
"""

from __future__ import annotations

import json
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

from scripts.task_run import task_run_muse_events as _muse_events  # noqa: E402
from scripts.task_run import task_run_support as _support  # noqa: E402

LANE_PHASES = ("CONTRACT-READ", "EDITING", "TESTING")

#: Typed stop marker the progress guard appends to the executor transcript
#: before killing a stalled lane. Parsed like `BLOCKED:` on the receipt.
NO_PROGRESS_STOP_PREFIX = "NO-PROGRESS-STOP:"


def lane_progress(stdout_text: str, stderr_text: str = "") -> dict[str, Any]:
    """Parse phase markers and the typed blocker from lane output (#815).

    Executors render progress on stderr while stdout carries the machine
    delivery: a lane whose stdout stayed empty still emitted CONTRACT-READ
    on stderr, so both streams are parsed (stdout first, stderr second).
    A guard-issued `NO-PROGRESS-STOP:` line parses as the blocker, like an
    executor-issued `BLOCKED:` line.
    """
    phases: list[str] = []
    blocker: str | None = None
    for text in (stdout_text, stderr_text):
        for line in _transcript_lines(text):
            stripped = line.strip()
            if stripped in LANE_PHASES and stripped not in phases:
                phases.append(stripped)
            elif blocker is None and stripped.startswith("BLOCKED:"):
                blocker = stripped[len("BLOCKED:"):].strip() or None
            elif blocker is None and stripped.startswith(NO_PROGRESS_STOP_PREFIX):
                blocker = stripped[len(NO_PROGRESS_STOP_PREFIX):].strip() or None
    return {"phases": phases, "blocker": blocker}


def _transcript_lines(text: str):
    """Expose phase text inside JSONL executor events as transcript lines."""
    agent_text = _muse_events.accumulated_agent_text(text)
    if agent_text:
        # Muse `--json` streams agent text as ordered delta chunks; one
        # marker line may span several chunks, so phases read the
        # accumulation, not any single chunk (#886).
        yield from agent_text.splitlines()
    for line in text.splitlines():
        yield line
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        yield from _event_texts(event)


def _event_texts(value: Any):
    if isinstance(value, Mapping):
        for key, nested in value.items():
            if key in {"text", "message", "content", "last_agent_message"} and isinstance(
                nested, str
            ):
                yield from nested.splitlines()
            else:
                yield from _event_texts(nested)
    elif isinstance(value, list):
        for nested in value:
            yield from _event_texts(nested)


def no_progress_stop_due(
    *,
    phases: Sequence[str],
    contract_read_at: float | None,
    now: float,
    budget_seconds: float,
    diff_present: bool | None,
) -> str | None:
    """Whether the no-progress guard must stop the lane now (#815).

    Pure in its inputs (including `now`) so tests drive it on a controlled
    clock: a require-change lane that announced `CONTRACT-READ` but shows no
    `EDITING` and no real scoped diff once the budget is spent is a typed
    stall, not a lane still worth its remaining timeout. An unobservable
    diff (`None`) suppresses the stop: the guard may only kill on an
    affirmative observed-absent worktree, never on a failed observation.
    """
    if budget_seconds <= 0:
        return None
    if "EDITING" in phases or diff_present:
        return None
    if diff_present is None:
        return None
    if "CONTRACT-READ" not in phases or contract_read_at is None:
        return None
    if now - contract_read_at < budget_seconds:
        return None
    return (
        "require-change lane produced no EDITING and no scoped diff within "
        f"{budget_seconds:g}s after CONTRACT-READ"
    )


def scoped_diff_present(
    worktree: Path, base_sha: str, scope_specs: Sequence[Mapping[str, Any]]
) -> bool | None:
    """Whether the worktree currently holds a real scoped diff.

    Reuses the checkpoint's own classification (refreshed specs plus the
    carrier's changed paths), so the live guard and the terminal checkpoint
    agree on what counts as progress. Three-valued: True/False for an
    observed worktree, None when the worktree cannot be observed — the guard
    must not kill a lane it cannot see.
    """
    try:
        refreshed = _support._refresh_scope_specs(worktree, list(scope_specs))
        changed = _support._candidate_carrier(worktree, base_sha)["changed_paths"]
        return bool(_support._paths_in_scopes(changed, refreshed))
    except Exception:  # noqa: BLE001 - an unobservable tree reads as unknown
        return None


def _worktree_liveliness(worktree: Path, base_sha: str) -> dict[str, Any] | None:
    """Changed files, lane-branch commits, and the last subject, or None when unobservable."""
    try:
        changed = _support._candidate_carrier(worktree, base_sha)["changed_paths"]
        log = _support._git(worktree, "log", f"{base_sha}..HEAD", "--format=%s")
        subjects = (
            [line.strip() for line in log.stdout.splitlines() if line.strip()]
            if log.returncode == 0
            else []
        )
    except Exception:  # noqa: BLE001 - an unobservable tree reads as unknown
        return None
    return {
        "files_changed": len(changed),
        "commits": len(subjects),
        "last_commit_subject": subjects[0][:120] if subjects else None,
    }
