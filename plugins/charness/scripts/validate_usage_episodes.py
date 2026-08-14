#!/usr/bin/env python3
"""Validate opt-in H-LAM/T usage episode JSONL records."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import jsonschema
import yaml
from usage_episode_records import read_valid_records
from usage_episode_records import resolve_records_path as _resolve_records_path
from usage_episode_records import schema_root as _schema_root

from runtime_bootstrap import repo_root_from_script
from yaml_output import emit_yaml

REPO_ROOT = repo_root_from_script(__file__)
DEFAULT_ADAPTER = Path(".agents/usage-episodes-adapter.yaml")
DEFAULT_STORAGE = Path(".charness/usage-episodes")
EVENT_FILENAME = "usage_episode.jsonl"


def _warning(warning_id: str, message: str, next_action: str) -> dict[str, str]:
    return {
        "warning_id": warning_id,
        "message": message,
        "next_action": next_action,
    }


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_adapter(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path}: adapter must be a mapping")
    return data


def _portable_path(repo_root: Path, path: Path) -> str:
    try:
        return str(path.resolve().relative_to(repo_root))
    except ValueError:
        return str(path)


def _no_records_payload(repo_root: Path, adapter_path: Path, records_path: Path) -> dict[str, Any]:
    return {
        "status": "no_records",
        "valid": True,
        "adapter_path": _portable_path(repo_root, adapter_path),
        "records_path": _portable_path(repo_root, records_path),
        "valid_count": 0,
        "errors": [],
        "warnings": [
            _warning(
                "usage_episodes_no_records",
                f"usage-episodes adapter at {_portable_path(repo_root, adapter_path)} is enabled but no records file exists yet at {_portable_path(repo_root, records_path)}",
                "Capture is opt-in; the records file is created on the first emitted episode. Disable the adapter if no capture is expected.",
            )
        ],
    }


def _emit_result(payload: dict[str, Any]) -> None:
    """Emit the result as YAML, carrying the retired human WARNING lines inside it.

    The status/count lines the human renderer printed were projections of
    `status`, `adapter_path`, `records_path`, `valid_count`, and `errors`, all of
    which the payload already holds. Its WARNING lines were not: `no_adapter`,
    `disabled`, and `no_records` are exit-ZERO attention states, and the prefixed
    line was the visible marker that an exit 0 here is not a validated corpus.
    That marker is folded into the payload rather than dropped -- which is also
    the `WARNING:` evidence term this file's entry in
    `skills/public/quality/references/attention-state-visibility.json` declares.
    """
    warnings = payload.get("warnings", [])
    if warnings:
        payload = {
            **payload,
            "attention": [
                f"WARNING: {warning['message']} Next action: {warning['next_action']}"
                for warning in warnings
            ],
        }
    emit_yaml(payload)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--adapter-path", type=Path)
    parser.add_argument("--records-path", type=Path)
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    adapter_path = args.adapter_path or repo_root / DEFAULT_ADAPTER
    if not adapter_path.is_absolute():
        adapter_path = repo_root / adapter_path
    schema_root = _schema_root(repo_root)
    manifest_schema = _load_json(schema_root / "manifest.schema.json")
    episode_schema = _load_json(schema_root / "episode.schema.json")

    if not adapter_path.is_file():
        payload = {
            "status": "no_adapter",
            "valid": True,
            "adapter_path": _portable_path(repo_root, adapter_path),
            "valid_count": 0,
            "errors": [],
            "warnings": [
                _warning(
                    "usage_episodes_adapter_missing",
                    f"no usage-episodes adapter found at {_portable_path(repo_root, adapter_path)}; validation skipped",
                    "Run setup seeding if this repo should opt into usage episode validation, or record the opt-out in quality closeout.",
                )
            ],
        }
        _emit_result(payload)
        return 0

    errors: list[str] = []
    try:
        adapter = _load_adapter(adapter_path)
        jsonschema.validate(adapter, manifest_schema)
    except (OSError, ValueError, yaml.YAMLError, jsonschema.ValidationError) as exc:
        payload = {
            "status": "invalid_adapter",
            "valid": False,
            "adapter_path": _portable_path(repo_root, adapter_path),
            "valid_count": 0,
            "errors": [str(exc)],
            "warnings": [],
        }
        _emit_result(payload)
        return 1

    if not adapter.get("enabled", False):
        payload = {
            "status": "disabled",
            "valid": True,
            "adapter_path": _portable_path(repo_root, adapter_path),
            "valid_count": 0,
            "errors": [],
            "warnings": [
                _warning(
                    "usage_episodes_adapter_disabled",
                    f"usage-episodes adapter at {_portable_path(repo_root, adapter_path)} is disabled; validation skipped",
                    "Keep the disabled state visible in quality closeout, or enable the adapter before relying on usage episode validation.",
                )
            ],
        }
        _emit_result(payload)
        return 0

    records_path = _resolve_records_path(repo_root, adapter, args.records_path)
    try:
        records_path.relative_to(repo_root)
    except ValueError:
        payload = {
            "status": "invalid_records_path",
            "valid": False,
            "adapter_path": _portable_path(repo_root, adapter_path),
            "records_path": _portable_path(repo_root, records_path),
            "valid_count": 0,
            "errors": ["records_path must stay under repo_root"],
            "warnings": [],
        }
        _emit_result(payload)
        return 1
    if not records_path.is_file():
        _emit_result(_no_records_payload(repo_root, adapter_path, records_path))
        return 0
    records, errors = read_valid_records(records_path, episode_schema)
    payload = {
        "status": "valid" if not errors else "invalid_records",
        "valid": not errors,
        "adapter_path": _portable_path(repo_root, adapter_path),
        "records_path": _portable_path(repo_root, records_path),
        "valid_count": len(records),
        "errors": errors,
        "warnings": [],
    }
    _emit_result(payload)
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
