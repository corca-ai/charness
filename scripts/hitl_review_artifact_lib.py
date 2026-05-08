from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from scripts.adapter_lib import load_yaml_file


def iso_from_ts(timestamp: float) -> str:
    return datetime.fromtimestamp(timestamp, timezone.utc).replace(microsecond=0).isoformat()


def portable_path(repo_root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(repo_root).as_posix()
    except ValueError:
        return f"external-path:{path.name}"


def session_dir_for(repo_root: Path, adapter: dict[str, Any], session_id: str | None) -> Path:
    runtime_root = repo_root / adapter["runtime_dir"]
    if session_id:
        path = runtime_root / session_id
        if not path.is_dir():
            raise RuntimeError(f"HITL runtime session not found: {portable_path(repo_root, path)}")
        return path
    sessions = [path for path in runtime_root.iterdir() if path.is_dir()] if runtime_root.is_dir() else []
    if not sessions:
        raise RuntimeError(f"No HITL runtime sessions found under {portable_path(repo_root, runtime_root)}")
    return max(sessions, key=lambda path: path.stat().st_mtime)


def _load_json_file(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {}


def _runtime_updated_at(session_dir: Path) -> tuple[float, str]:
    files = [path for path in session_dir.rglob("*") if path.is_file()]
    timestamp = max([session_dir.stat().st_mtime, *[path.stat().st_mtime for path in files]])
    return timestamp, iso_from_ts(timestamp)


def load_session(repo_root: Path, adapter: dict[str, Any], session_id: str | None) -> dict[str, Any]:
    session_dir = session_dir_for(repo_root, adapter, session_id)
    state_path = session_dir / "state.yaml"
    rules_path = session_dir / "rules.yaml"
    state = load_yaml_file(state_path) if state_path.is_file() else {}
    rules = load_yaml_file(rules_path) if rules_path.is_file() else {}
    queue = _load_json_file(session_dir / "queue.json")
    updated_ts, updated_iso = _runtime_updated_at(session_dir)
    sid = str(state.get("session_id") or queue.get("session_id") or session_dir.name)
    return {
        "session_id": sid,
        "session_dir": session_dir,
        "state": state,
        "rules": rules,
        "queue": queue,
        "runtime_updated_ts": updated_ts,
        "runtime_updated_at": updated_iso,
    }


def _as_items(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _accepted_rules(session: dict[str, Any]) -> list[Any]:
    return _as_items(session["state"].get("accepted_rules")) or _as_items(session["rules"].get("rules"))


def _digest(value: Any) -> str:
    rendered = json.dumps(value, ensure_ascii=False, sort_keys=True, default=str)
    return hashlib.sha256(rendered.encode("utf-8")).hexdigest()[:16]


def _queue_state_for_digest(queue: dict[str, Any]) -> dict[str, Any]:
    return {
        "current_queue_order": queue.get("current_queue_order", []),
        "reviewed_item_ids": queue.get("reviewed_item_ids", []),
        "superseded_unreviewed_item_ids": queue.get("superseded_unreviewed_item_ids", []),
        "completion_item_ids": queue.get("completion_item_ids", []),
        "applied_rewrite_review": queue.get("applied_rewrite_review"),
        "full_target_review": queue.get("full_target_review"),
    }


def _approval_state_for_digest(state: dict[str, Any]) -> dict[str, Any]:
    return {
        "active_rules_applied": state.get("active_rules_applied", []),
        "target_cursor_checked": state.get("target_cursor_checked"),
        "target_cursor_check_result": state.get("target_cursor_check_result", ""),
        "applied_rewrite_review_status": state.get("applied_rewrite_review_status", ""),
        "pending_rewrite_chunk_id": state.get("pending_rewrite_chunk_id", ""),
        "pending_rewrite_source_anchor": state.get("pending_rewrite_source_anchor", ""),
        "full_target_review_status": state.get("full_target_review_status", ""),
        "full_target_review_result": state.get("full_target_review_result", ""),
    }


def _first_pending_item(queue: dict[str, Any]) -> dict[str, Any] | None:
    finished = {"accepted", "applied", "deferred-to-spec", "superseded"}
    for item in _as_items(queue.get("items")):
        if isinstance(item, dict) and str(item.get("status", "pending")) not in finished:
            return item
    return None


def _next_chunk(state: dict[str, Any], queue: dict[str, Any]) -> Any:
    status = str(state.get("status") or queue.get("status") or "")
    if status in {"completed", "closed", "accepted"}:
        return "none"
    next_item = _first_pending_item(queue)
    return next_item.get("id") if next_item else state.get("last_presented_chunk_id") or "none"


def _lines_for_items(items: list[Any]) -> list[str]:
    lines: list[str] = []
    for item in items:
        if not isinstance(item, dict):
            lines.append(f"- {item}")
            continue
        item_id = item.get("id", "item")
        status = item.get("status", "pending")
        label = item.get("section") or item.get("type") or item.get("target") or ""
        line_span = item.get("lines") or item.get("line_span") or ""
        suffix = f" ({line_span})" if line_span else ""
        lines.append(f"- {item_id}: {status} {label}{suffix}".rstrip())
    return lines or ["- none"]


def _metadata(repo_root: Path, session: dict[str, Any]) -> dict[str, str]:
    state = session["state"]
    queue = session["queue"]
    return {
        "session_id": session["session_id"],
        "runtime_session_dir": portable_path(repo_root, session["session_dir"]),
        "runtime_updated_at": session["runtime_updated_at"],
        "target": str(state.get("target") or queue.get("target") or ""),
        "last_presented_chunk_id": str(state.get("last_presented_chunk_id", "")),
        "queue_epoch": str(state.get("queue_epoch") or queue.get("queue_epoch") or ""),
        "queue_status": str(state.get("queue_status") or queue.get("status") or ""),
        "accepted_rules_digest": _digest(_accepted_rules(session)),
        "queue_items_digest": _digest(_as_items(queue.get("items"))),
        "queue_state_digest": _digest(_queue_state_for_digest(queue)),
        "approval_state_digest": _digest(_approval_state_for_digest(state)),
    }


def check_runtime_phase(session: dict[str, Any], phase: str) -> list[str]:
    state = session["state"]
    errors: list[str] = []
    accepted_rules = _accepted_rules(session)
    active_rules = _as_items(state.get("active_rules_applied"))
    if phase in {"pre-edit", "cursor-advance"} and accepted_rules and not active_rules:
        errors.append("accepted rules are present but active_rules_applied is empty")
    if phase in {"pre-edit", "cursor-advance"} and state.get("target_cursor_checked") is not True:
        errors.append("target_cursor_checked must be true before editing or advancing")
    check_result = str(state.get("target_cursor_check_result") or "")
    target = str(state.get("target") or session["queue"].get("target") or "")
    chunk_id = str(state.get("last_presented_chunk_id") or "")
    queue_epoch = str(state.get("queue_epoch") or session["queue"].get("queue_epoch") or "")
    if phase in {"pre-edit", "cursor-advance"} and not check_result:
        errors.append("target_cursor_check_result must name target, chunk, queue item, line bounds, and epoch")
    if check_result:
        if target and target not in check_result:
            errors.append("target_cursor_check_result must name the current target")
        if chunk_id and chunk_id not in check_result:
            errors.append("target_cursor_check_result must name the current chunk id")
        if queue_epoch and queue_epoch not in check_result:
            errors.append("target_cursor_check_result must name the current queue epoch")
        if "line" not in check_result.lower():
            errors.append("target_cursor_check_result must name line bounds")
    if phase == "cursor-advance" and state.get("applied_rewrite_review_status") == "pending":
        errors.append("cannot advance while applied_rewrite_review_status is pending")
    return errors


def render_artifact(repo_root: Path, artifact_path: Path, session: dict[str, Any]) -> str:
    state = session["state"]
    queue = session["queue"]
    session_rel = portable_path(repo_root, session["session_dir"])
    target = str(state.get("target") or queue.get("target") or "")
    next_chunk = _next_chunk(state, queue)
    metadata = _metadata(repo_root, session)
    synced_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    return "\n".join(
        [
            "# HITL Runtime Checkpoint",
            "",
            "<!-- hitl-runtime-sync",
            *[f"{key}: {value}" for key, value in metadata.items()],
            "-->",
            "",
            f"- Synced At: {synced_at}",
            f"- Synced From Session: `{session['session_id']}`",
            f"- Runtime Session Dir: `{session_rel}`",
            f"- Runtime Updated At: {session['runtime_updated_at']}",
            "",
            "## Active Target",
            "",
            f"- Target: `{target or 'unknown'}`",
            f"- Status: `{state.get('status') or queue.get('status') or 'unknown'}`",
            f"- Last Presented Chunk ID: `{state.get('last_presented_chunk_id') or 'none'}`",
            f"- Queue Epoch: `{metadata['queue_epoch'] or 'unknown'}`",
            f"- Queue Status: `{metadata['queue_status'] or 'unknown'}`",
            f"- Explicit Apply Required: `{state.get('require_explicit_apply', queue.get('require_explicit_apply', True))}`",
            f"- Apply Mode: `{state.get('apply_mode') or queue.get('apply_mode') or 'unknown'}`",
            "",
            "## Accepted Rules",
            "",
            *_lines_for_items(_accepted_rules(session)),
            "",
            "## Queue State",
            "",
            f"- Current Queue Order: `{queue.get('current_queue_order', [])}`",
            f"- Reviewed Item IDs: `{queue.get('reviewed_item_ids', [])}`",
            f"- Superseded Unreviewed Item IDs: `{queue.get('superseded_unreviewed_item_ids', [])}`",
            "",
            "### Items",
            "",
            *_lines_for_items(_as_items(queue.get("items"))),
            "",
            "## Next Chunk To Present",
            "",
            f"- `{next_chunk}`",
            "",
            "## Approval Boundaries",
            "",
            f"- Applied Rewrite Review Status: `{state.get('applied_rewrite_review_status', 'unknown')}`",
            f"- Full Target Review Status: `{state.get('full_target_review_status', 'unknown')}`",
            f"- Target/Cursor Checked: `{state.get('target_cursor_checked', 'unknown')}`",
            f"- Target/Cursor Check Result: `{state.get('target_cursor_check_result', '')}`",
            "",
            "## Runtime Links",
            "",
            f"- State: `{session_rel}/state.yaml`",
            f"- Queue: `{session_rel}/queue.json`",
            f"- Rules: `{session_rel}/rules.yaml`",
            f"- Scratchpad: `{session_rel}/hitl-scratchpad.md`",
            f"- Events: `{session_rel}/events.log`",
            f"- Durable Artifact: `{portable_path(repo_root, artifact_path)}`",
            "",
        ]
    )


def parse_metadata(text: str) -> dict[str, str]:
    if "<!-- hitl-runtime-sync" not in text:
        return {}
    block = text.split("<!-- hitl-runtime-sync", 1)[1].split("-->", 1)[0]
    metadata: dict[str, str] = {}
    for line in block.splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            metadata[key.strip()] = value.strip()
    return metadata


def check_artifact(repo_root: Path, artifact_path: Path, session: dict[str, Any]) -> list[str]:
    if not artifact_path.is_file():
        return [f"missing durable artifact: {portable_path(repo_root, artifact_path)}"]
    metadata = parse_metadata(artifact_path.read_text(encoding="utf-8"))
    if not metadata:
        return ["durable artifact is missing hitl-runtime-sync metadata"]
    expected = _metadata(repo_root, session)
    errors = [
        f"{key} mismatch: durable={metadata.get(key)!r} runtime={value!r}"
        for key, value in expected.items()
        if metadata.get(key) != value
    ]
    if artifact_path.stat().st_mtime + 0.5 < session["runtime_updated_ts"]:
        errors.append("runtime changed after durable artifact sync")
    return errors
