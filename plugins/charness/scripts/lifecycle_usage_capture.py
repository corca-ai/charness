"""Capture verified issue/release lifecycle outcomes in the local usage stream.

This module is intentionally usable from both a source checkout and an installed
plugin.  Producers call :func:`capture_lifecycle_outcome` only after their own
remote/readback proof; this helper owns adapter/schema/privacy checks, stable
identities, and one append-mode write of the linked pair under the shared lock.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import sys
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import jsonschema
import yaml

DEFAULT_ADAPTER = Path(".agents/usage-episodes-adapter.yaml")
EVENT_FILENAME = "usage_episode.jsonl"
LIFECYCLE_KINDS = {"issue_close", "release_publish"}
_COMPACT_LOCATOR_CHARS = set("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789._:/#-")


def _load_sibling(repo_root: Path, name: str) -> dict[str, Any]:
    """Load a shared script beside this file without relying on ``PYTHONPATH``."""

    path = repo_root / "scripts" / f"{name}.py"
    if not path.is_file():
        path = Path(__file__).resolve().with_name(f"{name}.py")
    if str(path.parent) not in sys.path:
        sys.path.insert(0, str(path.parent))
    spec = importlib.util.spec_from_file_location(f"charness_lifecycle_{name}", path)
    if spec is None or spec.loader is None:
        raise ImportError(f"unable to load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.__dict__


def _schema_root(repo_root: Path) -> Path:
    candidate = repo_root / "integrations" / "usage-episodes"
    if (candidate / "manifest.schema.json").is_file() and (candidate / "episode.schema.json").is_file():
        return candidate
    # Installed plugins keep the integration beside their exported scripts.
    for parent in (Path(__file__).resolve().parents):
        candidate = parent / "integrations" / "usage-episodes"
        if (candidate / "manifest.schema.json").is_file() and (candidate / "episode.schema.json").is_file():
            return candidate
    raise FileNotFoundError("usage-episodes schemas are unavailable")


def episode_id_for(lifecycle_kind: str, evidence_locator: str, product_id: str = "") -> str:
    """Return the exact stable identity for one lifecycle/evidence pair."""

    semantic = f"{product_id}:{lifecycle_kind}:{evidence_locator}"
    digest = hashlib.sha256(semantic.encode("utf-8")).hexdigest()
    return f"episode-{digest}"


def _feedback_id_for(
    *, product_id: str, target_episode_id: str, feedback_signal: str,
    source_kind: str, evidence_ref: dict[str, str]
) -> str:
    feedback = _load_sibling(Path(__file__).resolve().parent.parent, "usage_episode_feedback")
    return feedback["feedback_id_for"](
        product_id=product_id,
        target_episode_id=target_episode_id,
        feedback_signal=feedback_signal,
        source_kind=source_kind,
        evidence_ref=evidence_ref,
    )


def _timestamp() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _portable_path(repo_root: Path, path: Path) -> str:
    try:
        return str(path.resolve().relative_to(repo_root))
    except ValueError:
        return str(path)


@contextmanager
def _stream_lock(records_path: Path):
    """Reuse the feedback writer's cross-platform advisory lock."""

    module = _load_sibling(Path(__file__).resolve().parent.parent, "record_usage_feedback")
    with module["_stream_lock"](records_path):
        yield


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _valid_adapter(adapter_path: Path, schema_root: Path) -> tuple[dict[str, Any] | None, str | None]:
    try:
        adapter = yaml.safe_load(adapter_path.read_text(encoding="utf-8"))
        if not isinstance(adapter, dict):
            raise ValueError("usage-episodes adapter must be a mapping")
        jsonschema.validate(adapter, _load_json(schema_root / "manifest.schema.json"))
    except (OSError, ValueError, yaml.YAMLError, jsonschema.ValidationError) as exc:
        return None, f"{exc.__class__.__name__}: {exc}"
    return adapter, None


def _privacy_ok(adapter: dict[str, Any]) -> bool:
    privacy = adapter.get("privacy")
    # ``privacy`` is optional in the manifest for compatibility with the
    # existing feedback writer. This helper carries no raw content; when the
    # section is present, the shared privacy contract still requires both raw
    # fields to be explicitly false.
    if privacy is None:
        return True
    if not isinstance(privacy, dict):
        return False
    return privacy.get("raw_prompt") is False and privacy.get("raw_transcript") is False


def _records_path(repo_root: Path, adapter: dict[str, Any]) -> tuple[Path | None, str | None]:
    raw = adapter.get("storage_path", ".charness/usage-episodes")
    storage = repo_root / raw if isinstance(raw, str) else repo_root / ".charness/usage-episodes"
    records = (storage / EVENT_FILENAME).resolve()
    try:
        records.relative_to(repo_root.resolve())
    except ValueError:
        return None, "storage_path must stay under repo_root"
    return records, None


def _episode_record(product_id: str, episode_id: str, locator: str, kind: str, timestamp: str) -> dict[str, Any]:
    issue = kind == "issue_close"
    return {
        "schema_version": 1,
        "event_type": "usage_episode",
        "timestamp": timestamp,
        "product_id": product_id,
        "episode_id": episode_id,
        "actor_kind": "agent",
        "context_bucket": "github_issue" if issue else "release",
        "entry_point": "command",
        "trigger_type": "explicit_request",
        "selected_job": "resolve_issue" if issue else "prepare_release",
        "core_action": "landed_verified_change" if issue else "published_release_surface",
        "agent_action": {"surface": "github_issue" if issue else "release_helper"},
        "first_value_ref": {"kind": "issue" if issue else "release", "ref": locator},
        "outcome_status": "delivered",
        "t_status": "none",
    }


def _feedback_record(product_id: str, episode_id: str, locator: str, kind: str, timestamp: str) -> dict[str, Any]:
    issue = kind == "issue_close"
    signal = "closed_issue" if issue else "released"
    source = "issue_lifecycle" if issue else "release_lifecycle"
    evidence = {"kind": "issue" if issue else "release", "ref": locator}
    return {
        "schema_version": 1,
        "event_type": "usage_feedback",
        "timestamp": timestamp,
        "product_id": product_id,
        "feedback_id": _feedback_id_for(
            product_id=product_id,
            target_episode_id=episode_id,
            feedback_signal=signal,
            source_kind=source,
            evidence_ref=evidence,
        ),
        "target_episode_id": episode_id,
        "feedback_signal": signal,
        "source_kind": source,
        "evidence_ref": evidence,
    }


def _append_pair_locked(
    *, repo_root: Path, records_path: Path, schema: dict[str, Any], delivery: dict[str, Any], feedback: dict[str, Any]
) -> dict[str, Any]:
    """Validate/replay under the shared lock, then write both lines once in append mode."""

    try:
        feedback_module = _load_sibling(Path(__file__).resolve().parent.parent, "usage_episode_feedback")
        records_module = _load_sibling(Path(__file__).resolve().parent.parent, "usage_episode_records")
        with _stream_lock(records_path):
            existing, errors = records_module["read_schema_valid_records"](records_path, schema)
            if errors:
                return {"status": "invalid_stream", "errors": errors}
            episode_id = str(delivery["episode_id"])
            feedback_id = str(feedback["feedback_id"])
            prior_delivery = next((row for row in existing if row.get("event_type") == "usage_episode" and row.get("episode_id") == episode_id), None)
            prior_feedback = next((row for row in existing if row.get("event_type") == "usage_feedback" and row.get("feedback_id") == feedback_id), None)
            if prior_delivery is not None or prior_feedback is not None:
                same_delivery = prior_delivery is not None and {k: prior_delivery[k] for k in delivery if k != "timestamp"} == {k: delivery[k] for k in delivery if k != "timestamp"}
                same_feedback = prior_feedback is not None and {k: prior_feedback[k] for k in feedback if k != "timestamp"} == {k: feedback[k] for k in feedback if k != "timestamp"}
                if same_delivery and same_feedback:
                    return {"status": "replay_noop", "episode_id": episode_id, "feedback_id": feedback_id, "appended": False, "errors": []}
                return {"status": "conflict", "episode_id": episode_id, "feedback_id": feedback_id, "appended": False, "errors": ["lifecycle identity already exists with different content"]}
            semantic_errors = feedback_module["semantic_feedback_errors"]([*existing, delivery, feedback])
            if semantic_errors:
                return {"status": "invalid_stream", "errors": semantic_errors}
            candidate = [*existing, delivery, feedback]
            validation_errors: list[str] = []
            validator = jsonschema.Draft7Validator(schema, format_checker=jsonschema.FormatChecker())
            for index, row in enumerate(candidate, start=1):
                validation_errors.extend(f"row {index}: {error.message}" for error in validator.iter_errors(row))
            if validation_errors:
                return {"status": "invalid_record", "episode_id": episode_id, "feedback_id": feedback_id, "appended": False, "errors": validation_errors}
            records_path.parent.mkdir(parents=True, exist_ok=True)
            # Keep this an O_APPEND write: slice-closeout capture predates this
            # helper and does not take the feedback lock. Replacing the whole
            # file here could lose a concurrent append from that producer.
            serialized = "".join(
                json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n"
                for row in (delivery, feedback)
            )
            with records_path.open("a", encoding="utf-8") as handle:
                handle.write(serialized)
                handle.flush()
                os.fsync(handle.fileno())
            return {"status": "appended", "episode_id": episode_id, "feedback_id": feedback_id, "appended": True, "records_path": _portable_path(repo_root, records_path), "errors": []}
    except Exception as exc:  # telemetry is best-effort after an external boundary
        return {"status": "capture_error", "appended": False, "errors": [f"{exc.__class__.__name__}: {exc}"]}


def capture_lifecycle_outcome(
    *, repo_root: Path, lifecycle_kind: str, evidence_locator: str, product_id: str | None = None
) -> dict[str, Any]:
    """Capture one verified lifecycle outcome; never raises for telemetry failures."""

    repo_root = repo_root.resolve()
    if lifecycle_kind not in LIFECYCLE_KINDS:
        return {"status": "invalid", "appended": False, "errors": [f"unsupported lifecycle kind: {lifecycle_kind}"]}
    if not evidence_locator or any(char not in _COMPACT_LOCATOR_CHARS for char in evidence_locator):
        return {"status": "invalid", "appended": False, "errors": ["evidence_locator must be compact and privacy-safe"]}
    try:
        schema_root = _schema_root(repo_root)
        adapter_path = repo_root / DEFAULT_ADAPTER
        if not adapter_path.is_file():
            return {"status": "no_adapter", "appended": False, "adapter_path": _portable_path(repo_root, adapter_path), "errors": []}
        adapter, adapter_error = _valid_adapter(adapter_path, schema_root)
        if adapter is None:
            return {"status": "invalid_adapter", "appended": False, "errors": [adapter_error or "invalid adapter"]}
        if not adapter.get("enabled", False) or not {"usage_episode", "usage_feedback"}.issubset(set(adapter.get("events", ["usage_episode", "usage_feedback"]))):
            return {"status": "disabled", "appended": False, "errors": []}
        if not _privacy_ok(adapter):
            return {"status": "invalid_adapter", "appended": False, "errors": ["privacy.raw_prompt and privacy.raw_transcript must both be false"]}
        if os.environ.get("CHARNESS_QUALITY_MODE"):
            return {"status": "readonly_quality_run", "appended": False, "errors": []}
        records_path, path_error = _records_path(repo_root, adapter)
        if records_path is None:
            return {"status": "invalid_storage_path", "appended": False, "errors": [path_error or "invalid storage path"]}
        resolved_product_id = product_id or str(adapter.get("repo") or repo_root.name)
        if not resolved_product_id or any(char not in _COMPACT_LOCATOR_CHARS for char in resolved_product_id):
            return {"status": "invalid", "appended": False, "errors": ["product_id must be compact and privacy-safe"]}
        episode_id = episode_id_for(lifecycle_kind, evidence_locator, resolved_product_id)
        timestamp = _timestamp()
        delivery = _episode_record(resolved_product_id, episode_id, evidence_locator, lifecycle_kind, timestamp)
        feedback = _feedback_record(resolved_product_id, episode_id, evidence_locator, lifecycle_kind, timestamp)
        result = _append_pair_locked(repo_root=repo_root, records_path=records_path, schema=_load_json(schema_root / "episode.schema.json"), delivery=delivery, feedback=feedback)
        result.update({"lifecycle_kind": lifecycle_kind, "evidence_locator": evidence_locator, "episode_id": episode_id, "feedback_id": feedback["feedback_id"]})
        return result
    except Exception as exc:
        return {"status": "capture_error", "appended": False, "errors": [f"{exc.__class__.__name__}: {exc}"]}


__all__ = ["capture_lifecycle_outcome", "episode_id_for"]
