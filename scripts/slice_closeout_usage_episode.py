#!/usr/bin/env python3

from __future__ import annotations

import json
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
USAGE_EPISODES_ADAPTER = Path(".agents/usage-episodes-adapter.yaml")
USAGE_EPISODES_DEFAULT_STORAGE = Path(".charness/usage-episodes")
USAGE_EPISODE_FILENAME = "usage_episode.jsonl"
USAGE_EPISODES_SESSIONS_CURRENT = Path(".charness/usage-episodes/sessions/current")
SESSION_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")


def _portable_path(repo_root: Path, path: Path) -> str:
    try:
        return str(path.resolve().relative_to(repo_root))
    except ValueError:
        return str(path)


def _usage_schema_root(repo_root: Path) -> Path:
    candidate = repo_root / "integrations" / "usage-episodes"
    if (candidate / "manifest.schema.json").is_file() and (candidate / "episode.schema.json").is_file():
        return candidate
    return REPO_ROOT / "integrations" / "usage-episodes"


def _usage_episode_timestamp() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _read_session_id(repo_root: Path) -> str | None:
    pointer = repo_root / USAGE_EPISODES_SESSIONS_CURRENT
    try:
        raw = pointer.read_text(encoding="utf-8").strip()
    except OSError:
        return None
    if not raw or not SESSION_ID_RE.match(raw):
        return None
    return raw


def _classify_t_signal(repo_root: Path) -> dict[str, object]:
    try:
        from scripts.classify_t_signal import classify_t_signal
    except ImportError:
        import importlib.util

        module_path = repo_root / "scripts" / "classify_t_signal.py"
        if not module_path.is_file():
            return {"t_status": "none", "skipped_reason": "diff_unavailable"}
        spec = importlib.util.spec_from_file_location("classify_t_signal", module_path)
        if spec is None or spec.loader is None:
            return {"t_status": "none", "skipped_reason": "diff_unavailable"}
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module.classify_t_signal(repo_root)
    return classify_t_signal(repo_root)


def _slice_closeout_episode(
    adapter: dict[str, object],
    status: str,
    repo_root: Path,
) -> dict[str, object]:
    episode_id = f"slice-closeout-{uuid.uuid4().hex}"
    episode: dict[str, object] = {
        "schema_version": 1,
        "event_type": "usage_episode",
        "timestamp": _usage_episode_timestamp(),
        "product_id": str(adapter.get("repo") or "charness"),
        "episode_id": episode_id,
        "actor_kind": "agent",
        "context_bucket": "repo_task",
        "entry_point": "command",
        "trigger_type": "explicit_request",
        "selected_job": "implement_slice",
        "core_action": "landed_verified_change",
        "agent_action": {
            "surface": "quality_gate",
            "capability_ref": "run_slice_closeout",
        },
        "first_value_ref": {
            "kind": "test_result",
            "ref": f"run_slice_closeout:{episode_id}:{status}",
        },
        "outcome_status": "delivered",
        "t_status": "none",
    }

    session_id = _read_session_id(repo_root)
    if session_id is not None:
        episode["session_id"] = session_id

    classification = _classify_t_signal(repo_root)
    t_status = classification.get("t_status", "none")
    if t_status != "none":
        episode["t_status"] = str(t_status)
        episode["t_evidence"] = {
            "rule_id": classification["rule_id"],
            "confidence": classification["confidence"],
            "matched_paths": classification["matched_paths"],
            "commit_refs": classification["commit_refs"],
            "diff_kind": classification["diff_kind"],
        }
    else:
        skipped_reason = classification.get("skipped_reason")
        if isinstance(skipped_reason, str) and skipped_reason:
            episode["classification_skipped"] = skipped_reason

    return episode


def _rotated_usage_episode_path(records_path: Path, index: int) -> Path:
    return records_path.with_name(f"{records_path.stem}.{index}{records_path.suffix}")


def _rotate_usage_episode_records(records_path: Path, rotation: object, pending_bytes: int) -> None:
    if not isinstance(rotation, dict):
        return
    max_size_mb = rotation.get("max_size_mb")
    if not isinstance(max_size_mb, int) or max_size_mb <= 0 or not records_path.exists():
        return
    max_size_bytes = max_size_mb * 1024 * 1024
    if records_path.stat().st_size + pending_bytes <= max_size_bytes:
        return

    max_files = rotation.get("max_files")
    keep_files = max_files if isinstance(max_files, int) and max_files > 0 else 1
    if keep_files == 1:
        records_path.unlink()
        return

    oldest = _rotated_usage_episode_path(records_path, keep_files - 1)
    if oldest.exists():
        oldest.unlink()
    for index in range(keep_files - 2, 0, -1):
        source = _rotated_usage_episode_path(records_path, index)
        if source.exists():
            source.rename(_rotated_usage_episode_path(records_path, index + 1))
    records_path.rename(_rotated_usage_episode_path(records_path, 1))


def emit_usage_episode_for_slice_closeout(repo_root: Path, status: str) -> dict[str, object]:
    adapter_path = repo_root / USAGE_EPISODES_ADAPTER
    if not adapter_path.is_file():
        return {
            "status": "no_adapter",
            "emitted": False,
            "adapter_path": _portable_path(repo_root, adapter_path),
        }

    try:
        import jsonschema
        import yaml

        schema_root = _usage_schema_root(repo_root)
        manifest_schema = json.loads((schema_root / "manifest.schema.json").read_text(encoding="utf-8"))
        episode_schema = json.loads((schema_root / "episode.schema.json").read_text(encoding="utf-8"))
        adapter = yaml.safe_load(adapter_path.read_text(encoding="utf-8"))
        if not isinstance(adapter, dict):
            raise ValueError("usage-episodes adapter must be a mapping")
        jsonschema.validate(adapter, manifest_schema)
    except Exception as exc:  # pragma: no cover - exercised through CLI behavior
        return {
            "status": "invalid_adapter",
            "emitted": False,
            "adapter_path": _portable_path(repo_root, adapter_path),
            "error": f"usage-episodes adapter is invalid: {exc.__class__.__name__}",
        }

    if not adapter.get("enabled", False):
        return {
            "status": "disabled",
            "emitted": False,
            "adapter_path": _portable_path(repo_root, adapter_path),
        }

    storage_path = adapter.get("storage_path")
    storage_dir = repo_root / storage_path if isinstance(storage_path, str) else repo_root / USAGE_EPISODES_DEFAULT_STORAGE
    records_path = (storage_dir / USAGE_EPISODE_FILENAME).resolve()
    try:
        records_path.relative_to(repo_root)
    except ValueError:
        return {
            "status": "invalid_records_path",
            "emitted": False,
            "adapter_path": _portable_path(repo_root, adapter_path),
            "records_path": _portable_path(repo_root, records_path),
            "error": "records_path must stay under repo_root",
        }

    episode = _slice_closeout_episode(adapter, status, repo_root)
    try:
        jsonschema.validate(episode, episode_schema)
        serialized = json.dumps(episode, ensure_ascii=False, sort_keys=True) + "\n"
        storage_dir.mkdir(parents=True, exist_ok=True)
        _rotate_usage_episode_records(records_path, adapter.get("rotation"), len(serialized.encode("utf-8")))
        with records_path.open("a", encoding="utf-8") as handle:
            handle.write(serialized)
    except Exception as exc:  # pragma: no cover - exercised through CLI behavior
        return {
            "status": "emit_failed",
            "emitted": False,
            "adapter_path": _portable_path(repo_root, adapter_path),
            "records_path": _portable_path(repo_root, records_path),
            "error": f"usage episode emission failed: {exc.__class__.__name__}",
        }

    return {
        "status": "emitted",
        "emitted": True,
        "adapter_path": _portable_path(repo_root, adapter_path),
        "records_path": _portable_path(repo_root, records_path),
        "episode_id": episode["episode_id"],
    }
