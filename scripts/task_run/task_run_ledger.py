"""Append task-run decisions to one repo-local v1 ledger."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any


def _load_repo_runtime_bootstrap():
    pathlib, sys = __import__("pathlib"), __import__("sys")
    marker = ("scripts", "adapter_lib.py")
    parents = pathlib.Path(__file__).resolve().parents
    root = next((p for p in parents if p.joinpath(*marker).is_file()), None)
    if root is not None and str(root) not in sys.path:
        sys.path.insert(0, str(root))


_load_repo_runtime_bootstrap()

from scripts.lessons.lesson_ledger_writer_lib import ledger_lock  # noqa: E402
from scripts.task_run import task_run_events  # noqa: E402

LEDGER_RELATIVE_PATH = Path("charness-artifacts/task-run/decision-ledger.jsonl")


def decision_ledger_path(repo_root: Path) -> Path:
    return repo_root.resolve() / LEDGER_RELATIVE_PATH


def decision_ledger_link(repo_root: Path) -> dict[str, Any]:
    path = decision_ledger_path(repo_root)
    return {
        "path": LEDGER_RELATIVE_PATH.as_posix(),
        "event_schema_version": task_run_events.EVENT_SCHEMA_VERSION,
        "exists": path.is_file(),
    }


def append_decision_event(repo_root: Path, event: object) -> dict[str, Any]:
    """Validate and append one unique decision event, then return its link."""
    normalized = task_run_events.validate_event(event)
    if normalized["source"] != "decision-ledger":
        raise task_run_events.EventSchemaError(
            "decision ledger accepts only source='decision-ledger' events"
        )
    path = decision_ledger_path(repo_root)
    encoded = json.dumps(normalized, ensure_ascii=False, separators=(",", ":"))
    with ledger_lock(path):
        path.parent.mkdir(parents=True, exist_ok=True)
        existing_ids: set[str] = set()
        if path.exists():
            for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                try:
                    existing = task_run_events.validate_event(json.loads(line))
                except (json.JSONDecodeError, task_run_events.EventSchemaError) as exc:
                    raise ValueError(
                        f"decision ledger has an invalid event at line {line_number}: {exc}"
                    ) from exc
                if existing["source"] != "decision-ledger":
                    raise ValueError(
                        f"decision ledger has a foreign event at line {line_number}"
                    )
                existing_ids.add(existing["event_id"])
        if normalized["event_id"] in existing_ids:
            raise ValueError(f"decision event already exists: {normalized['event_id']}")
        with path.open("a", encoding="utf-8") as handle:
            handle.write(encoded + "\n")
            handle.flush()
            os.fsync(handle.fileno())
    return decision_ledger_link(repo_root)


def read_decision_events(repo_root: Path) -> list[dict[str, Any]]:
    path = decision_ledger_path(repo_root)
    if not path.is_file():
        return []
    events: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        try:
            event = task_run_events.validate_event(json.loads(line))
        except (json.JSONDecodeError, task_run_events.EventSchemaError) as exc:
            raise ValueError(
                f"decision ledger has an invalid event at line {line_number}: {exc}"
            ) from exc
        if event["source"] != "decision-ledger":
            raise ValueError(f"decision ledger has a foreign event at line {line_number}")
        events.append(event)
    return events
