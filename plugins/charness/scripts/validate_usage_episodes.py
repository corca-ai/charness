#!/usr/bin/env python3
"""Validate opt-in H-LAM/T usage episode JSONL records."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import jsonschema
import yaml

from runtime_bootstrap import repo_root_from_script

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


def _schema_root(repo_root: Path) -> Path:
    candidate = repo_root / "integrations" / "usage-episodes"
    if (candidate / "manifest.schema.json").is_file() and (candidate / "episode.schema.json").is_file():
        return candidate
    return REPO_ROOT / "integrations" / "usage-episodes"


def _load_adapter(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path}: adapter must be a mapping")
    return data


def _storage_dir(repo_root: Path, adapter: dict[str, Any]) -> Path:
    raw = adapter.get("storage_path")
    if isinstance(raw, str) and raw:
        return repo_root / raw
    return repo_root / DEFAULT_STORAGE


def _portable_path(repo_root: Path, path: Path) -> str:
    try:
        return str(path.resolve().relative_to(repo_root))
    except ValueError:
        return str(path)


def _validate_jsonl(path: Path, episode_schema: dict[str, Any]) -> tuple[int, list[str]]:
    errors: list[str] = []
    valid_count = 0
    validator = jsonschema.Draft7Validator(episode_schema, format_checker=jsonschema.FormatChecker())
    if not path.is_file():
        return 0, [f"missing records file: {path}"]
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        stripped = line.strip()
        if not stripped:
            continue
        try:
            row = json.loads(stripped)
        except json.JSONDecodeError as exc:
            errors.append(f"{path}:{line_number}: invalid JSON: {exc}")
            continue
        try:
            validator.validate(row)
        except jsonschema.ValidationError as exc:
            path_text = ".".join(str(part) for part in exc.absolute_path)
            suffix = f" at {path_text}" if path_text else ""
            errors.append(f"{path}:{line_number}: schema error{suffix}: {exc.message}")
            continue
        timestamp = row.get("timestamp")
        if isinstance(timestamp, str):
            try:
                datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            except ValueError:
                errors.append(f"{path}:{line_number}: schema error at timestamp: {timestamp!r} is not date-time")
                continue
        valid_count += 1
    return valid_count, errors


def _print_result(payload: dict[str, Any], *, as_json: bool) -> None:
    if as_json:
        print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
        return
    for warning in payload.get("warnings", []):
        print(f"WARNING: {warning['message']} Next action: {warning['next_action']}")
    status = payload["status"]
    if status == "valid":
        print(f"Validated {payload['valid_count']} usage episode record(s).")
    elif status == "no_adapter":
        print(f"no_adapter: no adapter at {payload['adapter_path']}; validation skipped")
    elif status == "disabled":
        print(f"disabled: adapter at {payload['adapter_path']} has enabled:false; validation skipped")
    else:
        print(f"{status}: {len(payload.get('errors', []))} error(s)")
        for error in payload.get("errors", []):
            print(f"- {error}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--adapter-path", type=Path)
    parser.add_argument("--records-path", type=Path)
    parser.add_argument("--json", action="store_true")
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
        _print_result(payload, as_json=args.json)
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
        _print_result(payload, as_json=args.json)
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
        _print_result(payload, as_json=args.json)
        return 0

    records_path = args.records_path
    if records_path is None:
        records_path = _storage_dir(repo_root, adapter) / EVENT_FILENAME
    elif not records_path.is_absolute():
        records_path = repo_root / records_path
    records_path = records_path.resolve()
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
        _print_result(payload, as_json=args.json)
        return 1
    valid_count, errors = _validate_jsonl(records_path, episode_schema)
    payload = {
        "status": "valid" if not errors else "invalid_records",
        "valid": not errors,
        "adapter_path": _portable_path(repo_root, adapter_path),
        "records_path": _portable_path(repo_root, records_path),
        "valid_count": valid_count,
        "errors": errors,
        "warnings": [],
    }
    _print_result(payload, as_json=args.json)
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
