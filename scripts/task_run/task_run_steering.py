"""Typed lane steer queue and executor session continuation protocol."""
from __future__ import annotations

import json
import os
import uuid
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

STEER_ENVELOPE_KIND = "charness.task_steer.v1"
STEER_QUEUE_FILENAME = "steer.queue.jsonl"

def steer_queue_path(task_dir: Path) -> Path:
    """The one lane steer queue the CLI producer and both lane consumers share.

    The producer once wrote the task's private runtime directory while the
    progress poller and the executor loop read the task directory, so accepted
    messages never reached the lane (#883). Every site derives this path from
    the task directory through this owner.
    """
    return task_dir / STEER_QUEUE_FILENAME


def read_steer_queue(queue_path: Path) -> list[dict[str, Any]]:
    """Read the latest typed envelope for each message in the lane queue."""
    try:
        lines = queue_path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return []
    records: dict[str, dict[str, Any]] = {}
    for line in lines:
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(record, dict) and record.get("kind") == STEER_ENVELOPE_KIND:
            message_id = record.get("message_id")
            if isinstance(message_id, str):
                records[message_id] = record
    return list(records.values())


def enqueue_steer(
    queue_path: Path,
    task_id: str,
    message: str,
    *,
    reason: str | None = None,
    actor: str | None = None,
) -> dict[str, Any]:
    """Append a typed accept/nack envelope for one queued lane message.

    ``reason``/``actor`` are audit metadata supplied by the issuer;
    ``reason_code`` stays the machine disposition cause.
    """
    from scripts.task_run.task_run_runtime import utc_now_iso

    stamp = utc_now_iso()
    normalized = message.strip()
    record = {
        "kind": STEER_ENVELOPE_KIND,
        "message_id": str(uuid.uuid4()),
        "task_id": task_id,
        "message": normalized,
        "reason": reason,
        "actor": actor,
        "queued_at": stamp,
        "delivered_at": None,
        "disposition": "accepted" if normalized else "nacked",
        "reason_code": None if normalized else "empty-message",
        "resume_path": None,
    }
    if normalized:
        queue_path.parent.mkdir(parents=True, exist_ok=True)
        with queue_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
            handle.flush()
            os.fsync(handle.fileno())
    return record


def update_steer_queue(queue_path: Path, record: Mapping[str, Any]) -> None:
    """Append a delivery update; queue readers retain the newest version."""
    queue_path.parent.mkdir(parents=True, exist_ok=True)
    with queue_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(dict(record), ensure_ascii=False) + "\n")
        handle.flush()
        os.fsync(handle.fileno())


def steered_lane_invocation(
    executor: str,
    command: Sequence[str],
    prompt: str,
    messages: Sequence[Mapping[str, Any]],
    session_id: str | None,
) -> tuple[list[str], str, str]:
    """Build the next same-worktree invocation with typed messages in its prompt."""
    rendered = "\n\n[Charness steer messages]\n" + "\n".join(
        f"{item['message_id']} ({item['queued_at']}): {item['message']}"
        for item in messages
    )
    amended_prompt = prompt + rendered
    if executor == "claude" and session_id:
        resumed = list(command)
        if "--resume" in resumed:
            resumed[resumed.index("--resume") + 1] = session_id
        else:
            resumed.extend(["--resume", session_id])
        return resumed, amended_prompt, "session-resume"
    if executor == "muse" and session_id:
        prompt_path = Path(command[command.index("--prompt-file") + 1])
        prompt_path.write_text(amended_prompt, encoding="utf-8")
        return list(command), amended_prompt, "session-resume"
    if executor == "codex" and session_id:
        resume_options_start = command.index("-m")
        return (
            [
                *command[:resume_options_start],
                "resume",
                session_id,
                *command[resume_options_start:],
            ],
            amended_prompt,
            "session-resume",
        )
    return list(command), amended_prompt, "relaunch-in-place"
