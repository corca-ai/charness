"""Adapter normalization for the handoff chunker's issue-backed source."""
from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any


def _load_sibling(module_name: str):
    path = Path(__file__).resolve().parent / f"{module_name}.py"
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"{module_name}.py not found beside {Path(__file__).name}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def report_lines(value: Any) -> list[str]:
    """Normalize an installed adapter loader's diagnostic shape defensively."""
    if isinstance(value, (list, tuple)):
        return [str(item) for item in value]
    return [] if value is None else [str(value)]


def adapter_report(adapter: dict[str, Any]) -> dict[str, Any] | None:
    """Return a compact report only when a found adapter has something to say."""
    if adapter.get("found") is False:
        return None
    errors = report_lines(adapter.get("errors"))
    warnings = report_lines(adapter.get("warnings"))
    valid = adapter.get("valid")
    invalid = valid is False or (valid is None and bool(errors))
    if not invalid and not errors and not warnings:
        return None
    return {
        "valid": not invalid,
        "errors": errors,
        "warnings": warnings,
        "path": adapter.get("path"),
    }


def _adapter_yaml_loader():
    for ancestor in Path(__file__).resolve().parents:
        candidate = ancestor / "scripts" / "adapter_lib.py"
        if candidate.is_file():
            spec = importlib.util.spec_from_file_location(
                "handoff_issue_source_adapter_lib", candidate
            )
            if spec is None or spec.loader is None:
                continue
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module.load_yaml_file
    return None


def load_issue_source_config(
    repo_root: Path, *, default_issue_limit: int
) -> tuple[dict[str, Any], dict[str, Any] | None]:
    """Return normalized issue-source settings and any invalid-adapter report."""
    config = {
        "enabled": True,
        "limit": default_issue_limit,
        "repo": None,
        "labels_include": (),
        "labels_exclude": (),
        "exclude_numbers": (),
    }
    try:
        adapter = _load_sibling("resolve_adapter").load_adapter(repo_root)
        if adapter.get("valid") is False:
            config["enabled"] = False
            return config, adapter_report(adapter)
        adapter_path = adapter.get("path")
        if not adapter_path:
            return config, None
        load_yaml_file = _adapter_yaml_loader()
        if load_yaml_file is None:
            return config, None
        raw = load_yaml_file(Path(adapter_path))
        block = raw.get("issue_source") if isinstance(raw, dict) else None
        if not isinstance(block, dict):
            return config, None
    except Exception:
        return config, None

    if isinstance(block.get("enabled"), bool):
        config["enabled"] = block["enabled"]
    if isinstance(block.get("limit"), int) and block["limit"] > 0:
        config["limit"] = block["limit"]
    if isinstance(block.get("repo"), str) and block["repo"].strip():
        config["repo"] = block["repo"].strip()
    for key in ("labels_include", "labels_exclude"):
        value = block.get(key)
        if isinstance(value, list):
            config[key] = tuple(str(item) for item in value if isinstance(item, str))
    numbers = block.get("exclude_numbers")
    if isinstance(numbers, list):
        config["exclude_numbers"] = tuple(
            int(number) for number in numbers if isinstance(number, int)
        )
    return config, None
