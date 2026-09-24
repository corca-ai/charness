"""Terminalize a stale task-run exec only after confirming its runner is gone."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Sequence

from scripts.task_run import task_run_support as _support  # noqa: E402
from scripts.task_run.task_run import _terminal  # noqa: E402


def terminalize_stale_exec(
    runtime_path: Path,
    task_id: str,
    *,
    stale_before: float,
    dry_run: bool = False,
) -> dict[str, object]:
    """Interrupt an old lane only when its recorded runner is confirmed dead.

    ``stale_before`` is supplied by the retention owner so the active-window
    duration remains defined in one place. Persisted terminal state always goes
    through task_run.py's canonical ``_terminal`` writer.
    """
    if not math.isfinite(stale_before):
        raise ValueError("stale_before must be finite")
    result_path = _support.task_result_path(runtime_path, task_id)
    payload = _support.read_task_result(runtime_path, task_id)
    if payload is None:
        return {"transitioned": False, "reason": "record-missing"}
    if payload.get("phase") == "terminal":
        return {"transitioned": False, "reason": "already-terminal"}
    try:
        record_mtime = result_path.stat().st_mtime
    except OSError:
        return {"transitioned": False, "reason": "record-missing"}
    if record_mtime > stale_before:
        return {"transitioned": False, "reason": "record-fresh"}
    if _support.runner_liveness(payload).get("alive") is not False:
        return {"transitioned": False, "reason": "runner-not-confirmed-dead"}
    if dry_run:
        return {
            "transitioned": False,
            "would_transition": True,
            "reason": "dead-runner-and-stale-record",
            "status": "interrupted",
        }

    terminal = _terminal(
        payload,
        runtime_path,
        status="interrupted",
        error="The task-run runner exited before writing a terminal receipt.",
        next_step=(
            "The exec runner is no longer present and its lane record is outside the "
            "active window; inspect the retained worktree before retrying."
        ),
    )
    return {
        "transitioned": True,
        "reason": "dead-runner-and-stale-record",
        "task_id": task_id,
        "status": terminal["status"],
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Task-run lifecycle maintenance commands.")
    commands = parser.add_subparsers(dest="command", required=True)
    reap = commands.add_parser(
        "terminalize-stale-exec",
        help="write an interrupted terminal receipt for an old lane with a dead runner",
    )
    reap.add_argument("--runtime-root", type=Path, required=True)
    reap.add_argument("--task-id", required=True)
    reap.add_argument("--stale-before", type=float, required=True)
    reap.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    outcome = terminalize_stale_exec(
        args.runtime_root,
        args.task_id,
        stale_before=args.stale_before,
        dry_run=args.dry_run,
    )
    if outcome.get("transitioned") is True:
        action = "terminalized"
        reason = "dead runner and stale record; task_run.py::_terminal wrote interrupted"
        fields = {"status": "interrupted"}
    elif outcome.get("would_transition") is True:
        action = "would-terminalize"
        reason = "dead runner and stale record; task_run.py::_terminal would write interrupted"
        fields = {"status": "interrupted"}
    elif outcome.get("reason") == "runner-not-confirmed-dead":
        action = "skipped"
        reason = "runner is live or cannot be confirmed dead; lane left untouched"
        fields = {}
    elif outcome.get("reason") == "record-fresh":
        action = "skipped"
        reason = "lane record became fresh before terminalization; lane left untouched"
        fields = {}
    else:
        action = None
    if action is not None:
        outcome["log_entry"] = {"action": action, "reason": reason, "fields": fields}
    print(json.dumps(outcome, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
