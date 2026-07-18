from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "charness.release_observer.v1"


def _required_text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"release observer `{field}` must be a non-empty string")
    return value.strip()


def validate_release_observer_record(record: Any) -> dict[str, Any]:
    if not isinstance(record, dict):
        raise ValueError("release observer record must be an object")
    if record.get("schema_version") != SCHEMA_VERSION:
        raise ValueError(f"release observer `schema_version` must be `{SCHEMA_VERSION}`")
    target = record.get("target")
    if not isinstance(target, dict):
        raise ValueError("release observer `target` must be an object")
    for field in ("version", "tag", "commit", "release_url"):
        _required_text(target.get(field), f"target.{field}")
    channel = record.get("distinct_channel_verification")
    if not isinstance(channel, dict):
        raise ValueError("release observer `distinct_channel_verification` must be an object")
    _required_text(channel.get("channel"), "distinct_channel_verification.channel")
    _required_text(channel.get("status"), "distinct_channel_verification.status")
    installed = record.get("installed_readback")
    if not isinstance(installed, dict):
        raise ValueError("release observer `installed_readback` must be an object")
    _required_text(installed.get("status"), "installed_readback.status")
    non_claims = record.get("non_claims")
    if not isinstance(non_claims, list) or not non_claims:
        raise ValueError("release observer `non_claims` must be a non-empty list")
    for index, item in enumerate(non_claims):
        _required_text(item, f"non_claims[{index}]")
    return record


def _readback(repo_root: Path, *, command: str, run_shell) -> dict[str, Any]:
    command = (command or "").strip()
    if not command:
        return {
            "status": "unavailable",
            "command": None,
            "reason": "adapter readback command is not configured",
        }
    try:
        result = run_shell(command, cwd=repo_root, check=False)
    except Exception as exc:  # publication already happened; preserve a typed disposition
        return {
            "status": "unavailable",
            "command": command,
            "reason": f"{exc.__class__.__name__}: {exc}",
        }
    record: dict[str, Any] = {
        "status": "confirmed" if result.returncode == 0 else "unavailable",
        "command": command,
        "returncode": result.returncode,
    }
    if result.returncode == 0 and (stdout := (result.stdout or "").strip()):
        record["value"] = stdout.splitlines()[-1].strip()
    elif result.returncode != 0:
        record["reason"] = (result.stderr or result.stdout or "readback command failed").strip()[-500:]
    return record


def collect_installed_readback(
    repo_root: Path,
    *,
    install_refresh: dict[str, Any],
    version_command: str,
    doctor_command: str,
    run_shell,
) -> dict[str, Any]:
    version = _readback(repo_root, command=version_command, run_shell=run_shell)
    doctor = _readback(repo_root, command=doctor_command, run_shell=run_shell)
    statuses = {str(install_refresh.get("status", "unknown")), version["status"], doctor["status"]}
    status = "unavailable"
    if statuses <= {"refreshed", "confirmed"}:
        status = "observed"
    return {"status": status, "install_refresh": install_refresh, "version": version, "doctor": doctor}


def write_release_observer(
    repo_root: Path,
    *,
    payload: dict[str, Any],
    installed_readback: dict[str, Any],
    now=None,
) -> dict[str, Any]:
    channel = payload.get("distinct_channel_verification")
    release_url = payload.get("release_url") or payload.get("expected_release_url")
    record = {
        "schema_version": SCHEMA_VERSION,
        "observed_at": (now or (lambda: datetime.now(timezone.utc)))().isoformat(),
        "target": {
            "version": payload.get("target_version"),
            "tag": payload.get("tag_name"),
            "commit": payload.get("commit_sha"),
            "release_url": release_url,
        },
        "distinct_channel_verification": channel,
        "installed_readback": installed_readback,
        "non_claims": [
            "This record preserves observations; it is not a second release-success verdict.",
            "A digest, command exit code, or recorded status is not terminal proof of operator-facing behavior.",
        ],
    }
    validate_release_observer_record(record)
    date = record["observed_at"][:10]
    relpath = Path("charness-artifacts/probe") / f"{date}-{record['target']['tag']}-release-observer.json"
    path = repo_root / relpath
    path.parent.mkdir(parents=True, exist_ok=True)
    rendered = json.dumps(record, indent=2, sort_keys=True) + "\n"
    if not path.exists() or path.read_text(encoding="utf-8") != rendered:
        path.write_text(rendered, encoding="utf-8")
    return {"status": installed_readback["status"], "path": str(relpath), "record": record}


def safe_write_release_observer(
    repo_root: Path,
    *,
    payload: dict[str, Any],
    installed_readback: dict[str, Any],
    now=None,
) -> dict[str, Any]:
    """Keep already-published closeout moving while making persistence failure visible."""

    try:
        return write_release_observer(
            repo_root,
            payload=payload,
            installed_readback=installed_readback,
            now=now,
        )
    except Exception as exc:
        return {
            "status": "capture_error",
            "path": None,
            "reason": f"{exc.__class__.__name__}: {exc}",
            "non_claims": [
                "No durable release-observer JSON was persisted.",
                "This disposition does not change the canonical distinct-channel verdict.",
            ],
        }
