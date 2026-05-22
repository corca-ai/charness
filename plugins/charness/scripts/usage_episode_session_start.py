#!/usr/bin/env python3
"""SessionStart hook payload script for charness usage-episodes.

Installed into Claude (`~/.claude/settings.json`) and Codex
(`~/.codex/config.toml` or `hooks.json`) by `scripts/host_hook_install_lib.py`.
Reads the host-emitted JSON payload from stdin, walks up from the payload's
`cwd` to find `.agents/usage-episodes-adapter.yaml`, and — when the adapter is
opted in — writes a per-session `start.json` record plus refreshes the
`sessions/current` pointer used by the slice-closeout emitter.

Failure modes are intentionally silent: hook script errors must not break host
sessions. Set `CHARNESS_SESSION_START_DEBUG=1` to surface diagnostics on
stderr for debugging.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

ADAPTER_RELATIVE = Path(".agents/usage-episodes-adapter.yaml")
DEFAULT_STORAGE = Path(".charness/usage-episodes")
SESSIONS_SUBDIR = Path("sessions")
SESSION_START_FILENAME = "start.json"
CURRENT_POINTER_FILENAME = "current"
SCHEMA_VERSION = 1


def _debug(message: str) -> None:
    if os.environ.get("CHARNESS_SESSION_START_DEBUG", "").strip().lower() in {"1", "true", "yes", "on"}:
        print(f"usage_episode_session_start: {message}", file=sys.stderr)


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _read_payload(stream) -> dict[str, object]:
    try:
        raw = stream.read()
    except OSError as exc:
        _debug(f"stdin read failed: {exc}")
        return {}
    raw = (raw or "").strip()
    if not raw:
        return {}
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        _debug(f"stdin JSON decode failed: {exc}")
        return {}
    if not isinstance(payload, dict):
        _debug("stdin payload is not an object")
        return {}
    return payload


def _discover_repo_root(start: Path) -> Path | None:
    candidate = start.resolve()
    seen: set[Path] = set()
    while candidate not in seen:
        seen.add(candidate)
        if (candidate / ADAPTER_RELATIVE).is_file():
            return candidate
        if candidate.parent == candidate:
            return None
        candidate = candidate.parent
    return None


def _load_adapter(adapter_path: Path) -> dict[str, object] | None:
    try:
        import yaml  # type: ignore[import-untyped]
    except ImportError as exc:
        _debug(f"PyYAML unavailable: {exc}")
        return None
    try:
        data = yaml.safe_load(adapter_path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        _debug(f"adapter load failed: {exc}")
        return None
    if not isinstance(data, dict):
        _debug("adapter is not a mapping")
        return None
    return data


def _resolve_storage(repo_root: Path, adapter: dict[str, object]) -> Path:
    raw = adapter.get("storage_path")
    if isinstance(raw, str) and raw:
        return (repo_root / raw).resolve()
    return (repo_root / DEFAULT_STORAGE).resolve()


def _write_current_pointer(pointer_path: Path, session_id: str) -> None:
    try:
        from current_pointer_writer_lib import write_current_pointer_text
    except ImportError:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        from current_pointer_writer_lib import write_current_pointer_text  # type: ignore[no-redef]
    write_current_pointer_text(pointer_path, session_id + "\n")


def _record_start(
    *,
    storage_dir: Path,
    session_id: str,
    payload: dict[str, object],
    host: str,
) -> Path:
    sessions_dir = storage_dir / SESSIONS_SUBDIR / session_id
    sessions_dir.mkdir(parents=True, exist_ok=True)
    record = {
        "schema_version": SCHEMA_VERSION,
        "session_id": session_id,
        "hook_event_name": payload.get("hook_event_name"),
        "cwd": payload.get("cwd"),
        "model": payload.get("model"),
        "host": host,
        "timestamp": _now_iso(),
    }
    target = sessions_dir / SESSION_START_FILENAME
    tmp = target.with_name(f".{target.name}.tmp.{os.getpid()}")
    tmp.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(tmp, target)
    return target


def run(payload: dict[str, object], *, host: str, cwd_override: Path | None = None) -> dict[str, object]:
    cwd_raw = payload.get("cwd")
    cwd = cwd_override if cwd_override is not None else (Path(cwd_raw) if isinstance(cwd_raw, str) and cwd_raw else Path.cwd())
    repo_root = _discover_repo_root(cwd)
    if repo_root is None:
        _debug(f"no usage-episodes adapter found upward from {cwd}")
        return {"status": "no_adapter"}
    adapter = _load_adapter(repo_root / ADAPTER_RELATIVE)
    if adapter is None:
        return {"status": "adapter_unreadable"}
    if not adapter.get("enabled", False):
        return {"status": "disabled"}
    storage_dir = _resolve_storage(repo_root, adapter)
    try:
        storage_dir.relative_to(repo_root)
    except ValueError:
        _debug(f"storage_path escapes repo_root: {storage_dir}")
        return {"status": "invalid_storage_path"}
    session_id = uuid.uuid4().hex
    record_path = _record_start(
        storage_dir=storage_dir,
        session_id=session_id,
        payload=payload,
        host=host,
    )
    pointer_path = storage_dir / SESSIONS_SUBDIR / CURRENT_POINTER_FILENAME
    _write_current_pointer(pointer_path, session_id)
    return {
        "status": "recorded",
        "session_id": session_id,
        "record_path": str(record_path),
        "pointer_path": str(pointer_path),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", choices=["claude", "codex", "unknown"], default="unknown", help="Host that fired the hook; recorded into start.json for downstream analysis.")
    parser.add_argument("--cwd", type=Path, default=None, help="Override the cwd used for adapter discovery (debugging only).")
    args = parser.parse_args(argv)
    payload = _read_payload(sys.stdin)
    try:
        result = run(payload, host=args.host, cwd_override=args.cwd)
    except Exception as exc:  # pragma: no cover - never propagate hook errors
        _debug(f"unhandled error: {exc!r}")
        return 0
    _debug(f"result={result}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
