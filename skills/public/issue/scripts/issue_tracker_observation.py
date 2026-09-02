"""Immutable started/terminal receipts for one Goal Run provider mutation."""

from __future__ import annotations

import hashlib
import json
import os
import re
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ATTEMPT_ID_RE = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9._-]{0,127}$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


def _canonical_bytes(payload: dict[str, Any]) -> bytes:
    return (
        json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
    ).encode("utf-8")


def _with_receipt_hash(payload: dict[str, Any]) -> dict[str, Any]:
    unsigned = dict(payload)
    unsigned.pop("receipt_sha256", None)
    return {
        **unsigned,
        "receipt_sha256": hashlib.sha256(_canonical_bytes(unsigned)).hexdigest(),
    }


def _write_immutable(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise RuntimeError(f"provider observation already exists and is immutable: {path}")
    rendered = _canonical_bytes(payload)
    temporary: str | None = None
    try:
        with tempfile.NamedTemporaryFile(
            dir=path.parent, prefix=f".{path.name}.", delete=False
        ) as handle:
            temporary = handle.name
            handle.write(rendered)
            handle.flush()
            os.fsync(handle.fileno())
        os.link(temporary, path)
    except FileExistsError as exc:
        raise RuntimeError(f"provider observation already exists and is immutable: {path}") from exc
    finally:
        if temporary is not None:
            Path(temporary).unlink(missing_ok=True)


def _validated_dir(repo_root: Path, observation_dir: Path) -> Path:
    root = repo_root.resolve()
    target = observation_dir if observation_dir.is_absolute() else root / observation_dir
    resolved = target.resolve()
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise RuntimeError("provider observation directory must stay inside repo root") from exc
    return resolved


def _validated_identity(attempt_id: str, draft_sha256: str, binding_sha256: str) -> None:
    if not ATTEMPT_ID_RE.fullmatch(attempt_id):
        raise RuntimeError("attempt id contains unsupported characters")
    if not SHA256_RE.fullmatch(draft_sha256):
        raise RuntimeError("draft sha256 must be 64 lowercase hexadecimal characters")
    if not SHA256_RE.fullmatch(binding_sha256):
        raise RuntimeError("binding sha256 must be 64 lowercase hexadecimal characters")


def _read_receipt(path: Path) -> dict[str, Any] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return None
    if not isinstance(payload, dict):
        return None
    expected = payload.get("receipt_sha256")
    if (
        not isinstance(expected, str)
        or _with_receipt_hash(payload).get("receipt_sha256") != expected
    ):
        return None
    return payload


def read_attempt(
    *, repo_root: Path, observation_dir: Path, attempt_id: str
) -> dict[str, Any] | None:
    """Read one complete immutable observation pair with receipt binding."""
    if not ATTEMPT_ID_RE.fullmatch(attempt_id):
        return None
    directory = _validated_dir(repo_root, observation_dir)
    started_path = directory / f"{attempt_id}.started.json"
    terminal_path = directory / f"{attempt_id}.terminal.json"
    started = _read_receipt(started_path)
    terminal = _read_receipt(terminal_path)
    if started is None or terminal is None:
        return None
    root = repo_root.resolve()
    if (
        started.get("kind") != "charness.goal-run-observation/v1"
        or started.get("phase") != "started"
        or started.get("attempt_id") != attempt_id
        or terminal.get("kind") != "charness.goal-run-observation/v1"
        or terminal.get("phase") != "terminal"
        or terminal.get("attempt_id") != attempt_id
        or terminal.get("started_sha256") != started.get("receipt_sha256")
        or terminal.get("started_path") != str(started_path.relative_to(root))
        or (
            terminal.get("draft_sha256") is not None
            and terminal.get("draft_sha256") != started.get("draft_sha256")
        )
        or (
            terminal.get("binding_sha256") is not None
            and terminal.get("binding_sha256") != started.get("binding_sha256")
        )
    ):
        return None
    return {
        "started": {"path": str(started_path.relative_to(root)), "payload": started},
        "terminal": {"path": str(terminal_path.relative_to(root)), "payload": terminal},
    }


def find_close_attempts(
    *,
    repo_root: Path,
    observation_dir: Path,
    repo: str,
    parent_number: int,
    draft_sha256: str,
    binding_sha256: str,
    exclude_attempt_id: str,
) -> list[dict[str, Any]]:
    """Return every prior close start bound to the same Goal identity.

    Started-only or invalid-terminal records remain in the result with a null
    terminal so the caller cannot mistake an observation crash window for a
    mutation-free history.
    """
    directory = _validated_dir(repo_root, observation_dir)
    if not directory.is_dir():
        return []
    matches: list[dict[str, Any]] = []
    root = repo_root.resolve()
    for started_path in sorted(directory.glob("*.started.json")):
        attempt_id = started_path.name.removesuffix(".started.json")
        if attempt_id == exclude_attempt_id:
            continue
        started = _read_receipt(started_path)
        if started is None:
            continue
        parent = started.get("parent")
        if (
            started.get("kind") != "charness.goal-run-observation/v1"
            or started.get("phase") != "started"
            or started.get("attempt_id") != attempt_id
            or not isinstance(parent, dict)
            or not isinstance(parent.get("repo"), str)
            or parent["repo"].casefold() != repo.casefold()
            or parent.get("number") != parent_number
            or started.get("operation") not in {"close-goal-run", "resume-goal-run-close"}
            or started.get("draft_sha256") != draft_sha256
            or started.get("binding_sha256") != binding_sha256
        ):
            continue
        attempt = read_attempt(
            repo_root=repo_root,
            observation_dir=observation_dir,
            attempt_id=attempt_id,
        )
        matches.append(
            attempt
            or {
                "started": {
                    "path": str(started_path.relative_to(root)),
                    "payload": started,
                },
                "terminal": None,
            }
        )
    return matches


def find_unresolved_create(
    *,
    repo_root: Path,
    observation_dir: Path,
    repo: str,
    parent_number: int,
    work_item_key: str,
    submitted_body_sha256: str | None,
    exclude_attempt_id: str,
    compare_submitted_body: bool = True,
) -> dict[str, Any] | None:
    """Return an unresolved create; body digest comparison is legacy-only."""
    directory = _validated_dir(repo_root, observation_dir)
    if not directory.is_dir():
        return None
    for started_path in sorted(directory.glob("*.started.json")):
        started = _read_receipt(started_path)
        if started is None or started.get("attempt_id") == exclude_attempt_id:
            continue
        if (
            started.get("kind") != "charness.goal-run-observation/v1"
            or started.get("phase") != "started"
            or started.get("operation") != "create-child"
            or started.get("parent") != {"repo": repo, "number": parent_number}
            or started.get("target", {}).get("work_item_key") != work_item_key
        ):
            continue
        attempt_id = started.get("attempt_id")
        terminal_path = directory / f"{attempt_id}.terminal.json"
        terminal = _read_receipt(terminal_path)
        unresolved_reason: str | None = None
        if terminal is None:
            unresolved_reason = "terminal-observation-missing-or-invalid"
        elif terminal.get("started_sha256") != started.get("receipt_sha256") or terminal.get(
            "started_path"
        ) != str(started_path.relative_to(repo_root.resolve())):
            unresolved_reason = "terminal-observation-does-not-bind-started-receipt"
        elif terminal.get("mutation_invoked") and terminal.get("outcome") != "verified-write":
            unresolved_reason = "prior-mutation-outcome-unverified"
        if unresolved_reason is not None:
            return {
                "started_path": str(started_path.relative_to(repo_root.resolve())),
                "started_sha256": started.get("receipt_sha256"),
                "terminal_path": (
                    str(terminal_path.relative_to(repo_root.resolve()))
                    if terminal_path.exists()
                    else None
                ),
                "reason": unresolved_reason,
                **(
                    {
                        "prior_submitted_body_sha256": started.get("submitted_body_sha256"),
                        "requested_submitted_body_sha256": submitted_body_sha256,
                        "submitted_body_changed": (
                            started.get("submitted_body_sha256") != submitted_body_sha256
                        ),
                    }
                    if compare_submitted_body
                    else {}
                ),
            }
    return None


def begin(
    *,
    repo_root: Path,
    observation_dir: Path,
    attempt_id: str,
    draft_sha256: str,
    binding_sha256: str,
    repo: str,
    parent_number: int,
    operation: str,
    target: dict[str, Any],
    submitted_body_sha256: str | None,
    backend: dict[str, Any],
) -> dict[str, Any]:
    _validated_identity(attempt_id, draft_sha256, binding_sha256)
    directory = _validated_dir(repo_root, observation_dir)
    path = directory / f"{attempt_id}.started.json"
    payload = _with_receipt_hash(
        {
            "kind": "charness.goal-run-observation/v1",
            "phase": "started",
            "observed_at": datetime.now(timezone.utc).isoformat(),
            "attempt_id": attempt_id,
            "draft_sha256": draft_sha256,
            "binding_sha256": binding_sha256,
            "parent": {"repo": repo, "number": parent_number},
            "operation": operation,
            "target": target,
            "submitted_body_sha256": submitted_body_sha256,
            "backend": {"id": backend.get("id"), "binary": backend.get("binary")},
            "outcome": "started",
            "mutation_invoked": False,
        }
    )
    _write_immutable(path, payload)
    return {"path": str(path.relative_to(repo_root.resolve())), "payload": payload}


def finish(
    *,
    repo_root: Path,
    observation_dir: Path,
    attempt_id: str,
    started: dict[str, Any],
    result: dict[str, Any],
) -> dict[str, Any]:
    directory = _validated_dir(repo_root, observation_dir)
    path = directory / f"{attempt_id}.terminal.json"
    payload = _with_receipt_hash(
        {
            "kind": "charness.goal-run-observation/v1",
            "phase": "terminal",
            "observed_at": datetime.now(timezone.utc).isoformat(),
            "attempt_id": attempt_id,
            "draft_sha256": started["payload"]["draft_sha256"],
            "binding_sha256": started["payload"]["binding_sha256"],
            "started_path": started["path"],
            "started_sha256": started["payload"]["receipt_sha256"],
            "outcome": result.get("outcome"),
            "mutation_invoked": bool(result.get("mutation_invoked")),
            "result": result,
        }
    )
    _write_immutable(path, payload)
    return {"path": str(path.relative_to(repo_root.resolve())), "payload": payload}
