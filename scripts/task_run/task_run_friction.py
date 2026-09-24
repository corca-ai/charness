"""Append task-run friction events and classify repeated event kinds."""

from __future__ import annotations

import json
import os
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Mapping


def _load_repo_runtime_bootstrap():
    pathlib, sys = __import__("pathlib"), __import__("sys")
    marker = ("scripts", "adapter_lib.py")
    parents = pathlib.Path(__file__).resolve().parents
    root = next((p for p in parents if p.joinpath(*marker).is_file()), None)
    if root is not None and str(root) not in sys.path:
        sys.path.insert(0, str(root))


_load_repo_runtime_bootstrap()

from scripts.lessons.lesson_ledger_writer_lib import ledger_lock  # noqa: E402
from scripts.task_run import task_run_events, task_run_runtime  # noqa: E402

FRICTION_LOG_RELATIVE_PATH = Path("task-run/friction-log.jsonl")
FRICTION_WINDOW = timedelta(days=30)
PATTERN_REPAIR_ESCALATION = "repair the pattern, don't reshape the command"


def friction_log_path(runtime_path: Path) -> Path:
    """Return the machine-local append-only log beside task-run results."""
    return runtime_path / FRICTION_LOG_RELATIVE_PATH


def _read_events(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    events = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        try:
            event = task_run_events.validate_event(json.loads(line))
        except (json.JSONDecodeError, task_run_events.EventSchemaError) as exc:
            raise ValueError(f"friction log has an invalid event at line {line_number}: {exc}") from exc
        if event["source"] != "friction-log":
            raise ValueError(f"friction log has a foreign event at line {line_number}")
        events.append(event)
    return events


def _timestamp(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def append_friction_event(
    runtime_path: Path,
    event_kind: str,
    *,
    task_id: str,
    facts: Mapping[str, Any] | None = None,
    occurred_at: str | None = None,
) -> dict[str, Any] | None:
    """Append one validated event; repeat kinds in 30 days carry escalation."""
    stamp = occurred_at or task_run_runtime.utc_now_iso()
    event_facts = dict(facts or {})
    event_facts["task_id"] = task_id
    event = {
        "schema_version": task_run_events.EVENT_SCHEMA_VERSION,
        "event_id": str(uuid.uuid4()),
        "occurred_at": stamp,
        "source": "friction-log",
        "event_kind": event_kind,
        "facts": event_facts,
    }
    try:
        normalized = task_run_events.validate_event(event)
        path = friction_log_path(runtime_path)
        with ledger_lock(path):
            previous = _read_events(path)
            current_time = _timestamp(stamp)
            cutoff = current_time - FRICTION_WINDOW
            matches = [
                prior
                for prior in previous
                if prior["event_kind"] == event_kind
                and prior["facts"].get("task_id") != task_id
                and cutoff <= _timestamp(prior["occurred_at"]) <= current_time
            ]
            if matches:
                normalized["facts"]["escalation"] = PATTERN_REPAIR_ESCALATION
                normalized["facts"]["matching_event_ids"] = [item["event_id"] for item in matches]
            encoded = json.dumps(normalized, ensure_ascii=False, separators=(",", ":"))
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open("a", encoding="utf-8") as handle:
                handle.write(encoded + "\n")
                handle.flush()
                os.fsync(handle.fileno())
        return normalized
    except (OSError, ValueError):
        # Logging must not change lane runtime semantics when its local store is unavailable.
        return None


def append_terminal_friction(runtime_path: Path, payload: Mapping[str, Any]) -> None:
    """Record terminal blocks and retry-shaped outcomes from the task receipt."""
    status = payload.get("status")
    if status == "premise-blocked":
        prelaunch = payload.get("prelaunch")
        critique = prelaunch.get("brief_critique") if isinstance(prelaunch, Mapping) else None
        if isinstance(critique, Mapping) and critique.get("premise_failure"):
            return  # the prelaunch producer already wrote the premise-failure event
        event_kind = "block"
    elif status in {"interrupted", "timed-out", "executor-unavailable"}:
        event_kind = "relaunch"
    elif status == "failed":
        event_kind = "block"
    else:
        return
    append_friction_event(
        runtime_path,
        event_kind,
        task_id=str(payload.get("task_id") or "unknown-task"),
        facts={
            "status": status,
            "blocker": str(payload.get("blocker") or "")[:500],
            "next_step": str(payload.get("next_step") or "")[:500],
            "producer": "task_run",
        },
    )


def append_execution_friction(
    runtime_path: Path,
    *,
    task_id: str,
    relaunch_count: int,
    execution_error: str | None,
) -> None:
    """Record each executor reinvocation and any terminal invocation error."""
    for invocation in range(1, relaunch_count + 1):
        append_friction_event(
            runtime_path,
            "relaunch",
            task_id=task_id,
            facts={"producer": "task_run_execution", "invocation": invocation},
        )
    if execution_error:
        append_friction_event(
            runtime_path,
            "block",
            task_id=task_id,
            facts={
                "producer": "task_run_execution",
                "error": str(execution_error)[:500],
            },
        )


def append_completion_friction(
    runtime_path: Path,
    *,
    task_id: str,
    blockers: list[str],
    parent_classification: str,
) -> None:
    """Record final blockers, marking writer conflicts for manual resolution."""
    if parent_classification != "writer-conflict" and not blockers:
        return
    event_kind = "conflict-resolution" if parent_classification == "writer-conflict" else "block"
    append_friction_event(
        runtime_path,
        event_kind,
        task_id=task_id,
        facts={
            "producer": "task_run_completion",
            "parent_classification": parent_classification,
            "resolution": "operator-needed" if event_kind == "conflict-resolution" else None,
            "blockers": [str(item)[:500] for item in blockers[:20]],
        },
    )
