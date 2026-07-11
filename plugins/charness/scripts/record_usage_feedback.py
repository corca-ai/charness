#!/usr/bin/env python3
"""Preview or append one privacy-safe feedback event to a usage-episode stream."""

from __future__ import annotations

import argparse
import json
import os
import sys
from contextlib import contextmanager, nullcontext
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import fcntl
except ImportError:  # pragma: no cover - exercised on Windows hosts
    fcntl = None

try:
    import msvcrt
except ImportError:  # pragma: no cover - exercised on POSIX hosts
    msvcrt = None

import jsonschema
import yaml
from usage_episode_feedback import (
    FEEDBACK_SIGNALS,
    SOURCE_KINDS,
    feedback_id_for,
    semantic_feedback_errors,
    signal_allowed_for_source,
)
from usage_episode_records import read_schema_valid_records, resolve_records_path
from usage_episode_records import schema_root as _schema_root

DEFAULT_ADAPTER = Path(".agents/usage-episodes-adapter.yaml")


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _portable_path(repo_root: Path, path: Path) -> str:
    try:
        return str(path.resolve().relative_to(repo_root))
    except ValueError:
        return str(path)


def _timestamp() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


class FeedbackLockError(RuntimeError):
    """Raised when the usage-feedback stream cannot be serialized safely."""


@contextmanager
def _stream_lock(records_path: Path):
    """Serialize feedback read/validate/replay/append operations per stream.

    The lock is a stable sibling file, so it survives writer process exit and
    cannot be split into multiple inodes by cleanup between two writers.  Use
    the platform's standard advisory locking primitive instead of adding a
    runtime dependency: ``fcntl.flock`` on POSIX and ``msvcrt.locking`` on
    Windows.  A platform without either primitive fails closed rather than
    risking duplicate feedback events.
    """

    lock_path = records_path.with_name(f".{records_path.name}.lock")
    try:
        lock_path.parent.mkdir(parents=True, exist_ok=True)
        handle = lock_path.open("a+", encoding="utf-8")
    except OSError as exc:
        raise FeedbackLockError(f"unable to lock usage-feedback stream: {exc}") from exc
    with handle:
        if fcntl is not None:
            try:
                fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
            except OSError as exc:
                raise FeedbackLockError(f"unable to lock usage-feedback stream: {exc}") from exc
            body_failed = False
            try:
                yield
            except BaseException:
                body_failed = True
                raise
            finally:
                try:
                    fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
                except OSError as exc:
                    # Preserve an exception raised by the critical-section body;
                    # only report unlock failure when no body exception is active.
                    if not body_failed:
                        raise FeedbackLockError(f"unable to unlock usage-feedback stream: {exc}") from exc
            return
        if msvcrt is not None:
            try:
                # ``msvcrt.locking`` needs an existing byte at the lock
                # offset.  All writers use byte zero of the stable lock file.
                handle.seek(0, os.SEEK_END)
                if handle.tell() == 0:
                    handle.write("0")
                    handle.flush()
                handle.seek(0)
                msvcrt.locking(handle.fileno(), msvcrt.LK_LOCK, 1)
            except OSError as exc:
                raise FeedbackLockError(f"unable to lock usage-feedback stream: {exc}") from exc
            body_failed = False
            try:
                yield
            except BaseException:
                body_failed = True
                raise
            finally:
                try:
                    handle.seek(0)
                    msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
                except OSError as exc:
                    if not body_failed:
                        raise FeedbackLockError(f"unable to unlock usage-feedback stream: {exc}") from exc
            return
    raise FeedbackLockError("no supported platform file-locking primitive is available")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--adapter-path", type=Path)
    parser.add_argument("--product-id", required=True)
    parser.add_argument("--target-episode-id", required=True)
    parser.add_argument("--feedback-signal", choices=sorted(FEEDBACK_SIGNALS), required=True)
    parser.add_argument("--source-kind", choices=sorted(SOURCE_KINDS), required=True)
    parser.add_argument("--evidence-kind", choices=["artifact", "issue", "release", "review"], required=True)
    parser.add_argument("--evidence-ref", required=True)
    parser.add_argument("--execute", action="store_true", help="Append the event; default is a no-write preview.")
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def _print(payload: dict[str, Any], as_json: bool) -> None:
    if as_json:
        print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(f"{payload['status']}: feedback_id={payload.get('feedback_id', '<none>')}")
        for error in payload.get("errors", []):
            print(f"- {error}")


def _run_feedback_transaction(
    *,
    repo_root: Path,
    records_path: Path,
    storage: Path,
    schema: dict[str, Any],
    record: dict[str, Any],
    feedback_id: str,
    execute: bool,
    as_json: bool,
) -> int:
    lock = _stream_lock(records_path) if execute else nullcontext()
    try:
        # For an execute, this entire read/validate/replay/append sequence is
        # one critical section.  A second identical writer therefore observes
        # the first row and returns replay_noop instead of appending a duplicate.
        with lock:
            existing, read_errors = read_schema_valid_records(records_path, schema)
            if read_errors:
                _print({"status": "invalid_feedback", "executed": False, "feedback_id": feedback_id, "errors": read_errors}, as_json)
                return 2
            errors = semantic_feedback_errors([*existing, record])
            replay = next((item for item in existing if item.get("event_type") == "usage_feedback" and item.get("feedback_id") == feedback_id), None)
            if replay is not None:
                if {key: replay[key] for key in record if key != "timestamp"} == {key: record[key] for key in record if key != "timestamp"}:
                    _print({"status": "replay_noop", "executed": False, "feedback_id": feedback_id, "records_path": _portable_path(repo_root, records_path), "errors": []}, as_json)
                    return 0
                _print({"status": "conflicting_feedback_id", "executed": False, "feedback_id": feedback_id, "errors": errors}, as_json)
                return 2
            if errors:
                _print({"status": "invalid_feedback", "executed": False, "feedback_id": feedback_id, "errors": errors}, as_json)
                return 2
            payload = {"status": "dry_run", "executed": False, "feedback_id": feedback_id, "record": record, "records_path": _portable_path(repo_root, records_path), "errors": []}
            if execute:
                serialized = json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n"
                storage.mkdir(parents=True, exist_ok=True)
                # Do not rotate this mixed stream here: moving a delivery out of the
                # active file before appending linked feedback would make the validator
                # see an unlinked target. Stream-aware multi-file reconciliation is a
                # later retention seam; feedback append preserves link integrity now.
                with records_path.open("a", encoding="utf-8") as handle:
                    handle.write(serialized)
                payload.update({"status": "appended", "executed": True})
            _print(payload, as_json)
            return 0
    except FeedbackLockError as exc:
        _print({"status": "feedback_lock_error", "executed": False, "feedback_id": feedback_id, "errors": [str(exc)]}, as_json)
        return 2


def main() -> int:
    args = _parse_args()
    repo_root = args.repo_root.resolve()
    if not signal_allowed_for_source(args.source_kind, args.feedback_signal):
        _print({"status": "invalid_feedback", "executed": False, "errors": ["feedback_signal is not permitted for source_kind"]}, args.json)
        return 2
    if args.execute and os.environ.get("CHARNESS_QUALITY_MODE"):
        _print({"status": "readonly_quality_run", "executed": False, "errors": ["quality mode forbids feedback writes"]}, args.json)
        return 2
    adapter_path = args.adapter_path or repo_root / DEFAULT_ADAPTER
    if not adapter_path.is_absolute():
        adapter_path = repo_root / adapter_path
    if not adapter_path.is_file():
        _print({"status": "no_adapter", "executed": False, "errors": ["usage-episodes adapter is required"]}, args.json)
        return 2
    try:
        adapter = yaml.safe_load(adapter_path.read_text(encoding="utf-8"))
        if not isinstance(adapter, dict):
            raise ValueError("usage-episodes adapter must be a mapping")
        schema_root = _schema_root(repo_root)
        jsonschema.validate(adapter, _load_json(schema_root / "manifest.schema.json"))
    except (OSError, ValueError, yaml.YAMLError, jsonschema.ValidationError) as exc:
        _print({"status": "invalid_adapter", "executed": False, "errors": [str(exc)]}, args.json)
        return 2
    if not adapter.get("enabled", False) or "usage_feedback" not in adapter.get("events", ["usage_episode", "usage_feedback"]):
        _print({"status": "disabled", "executed": False, "errors": ["usage_feedback is not enabled by the adapter"]}, args.json)
        return 2
    records_path = resolve_records_path(repo_root, adapter, None)
    storage = records_path.parent
    try:
        records_path.relative_to(repo_root)
    except ValueError:
        _print({"status": "invalid_records_path", "executed": False, "errors": ["records_path must stay under repo_root"]}, args.json)
        return 2
    evidence_ref = {"kind": args.evidence_kind, "ref": args.evidence_ref}
    feedback_id = feedback_id_for(product_id=args.product_id, target_episode_id=args.target_episode_id, feedback_signal=args.feedback_signal, source_kind=args.source_kind, evidence_ref=evidence_ref)
    record = {"schema_version": 1, "event_type": "usage_feedback", "timestamp": _timestamp(), "product_id": args.product_id, "feedback_id": feedback_id, "target_episode_id": args.target_episode_id, "feedback_signal": args.feedback_signal, "source_kind": args.source_kind, "evidence_ref": evidence_ref}
    schema = _load_json(schema_root / "episode.schema.json")
    try:
        jsonschema.validate(record, schema, format_checker=jsonschema.FormatChecker())
    except jsonschema.ValidationError as exc:
        _print({"status": "invalid_feedback", "executed": False, "feedback_id": feedback_id, "errors": [str(exc)]}, args.json)
        return 2
    return _run_feedback_transaction(
        repo_root=repo_root,
        records_path=records_path,
        storage=storage,
        schema=schema,
        record=record,
        feedback_id=feedback_id,
        execute=args.execute,
        as_json=args.json,
    )


if __name__ == "__main__":
    sys.exit(main())
