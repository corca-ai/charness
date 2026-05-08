#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
from typing import Any


def _load_skill_runtime_bootstrap():
    script_path = Path(__file__).resolve()
    for ancestor in script_path.parents:
        candidate = ancestor / "skill_runtime_bootstrap.py"
        if candidate.is_file():
            spec = importlib.util.spec_from_file_location("skill_runtime_bootstrap", candidate)
            if spec is None or spec.loader is None:
                continue
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module
    raise ImportError("skill_runtime_bootstrap.py not found")


SKILL_RUNTIME = _load_skill_runtime_bootstrap()
REPO_ROOT = SKILL_RUNTIME.repo_root_from_skill_script(__file__)
_adapter_lib_module = SKILL_RUNTIME.load_repo_module_from_skill_script(__file__, "scripts.adapter_lib")
load_yaml_file = _adapter_lib_module.load_yaml_file

ADAPTER_CANDIDATES = (
    Path(".agents/issue-adapter.yaml"),
    Path(".codex/issue-adapter.yaml"),
    Path(".claude/issue-adapter.yaml"),
    Path("docs/issue-adapter.yaml"),
    Path("issue-adapter.yaml"),
)


def infer_defaults() -> dict[str, Any]:
    return {
        "version": 1,
        "default_org": "corca-ai",
        "default_repo": None,
        "remote_name": "origin",
    }


def _string(value: Any, field: str, errors: list[str]) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{field} must be a non-empty string")
        return None
    return value


def find_adapter(repo_root: Path) -> Path | None:
    for candidate in ADAPTER_CANDIDATES:
        path = repo_root / candidate
        if path.is_file():
            return path
    return None


def load_adapter(repo_root: Path) -> dict[str, Any]:
    searched_paths = [str((repo_root / candidate).resolve()) for candidate in ADAPTER_CANDIDATES]
    adapter_path = find_adapter(repo_root)
    defaults = infer_defaults()
    if adapter_path is None:
        return {
            "found": False,
            "valid": True,
            "path": None,
            "data": defaults,
            "errors": [],
            "warnings": [
                "No issue adapter found. Using default_org=corca-ai and current-repo inference.",
                "Create .agents/issue-adapter.yaml to change default GitHub ownership, default repo, or labels.",
            ],
            "searched_paths": searched_paths,
        }

    raw = load_yaml_file(adapter_path)
    raw_data = raw if isinstance(raw, dict) else {}
    data = dict(defaults)
    errors: list[str] = []
    warnings: list[str] = []
    if not isinstance(raw, dict):
        warnings.append("Adapter file did not contain a mapping. Using inferred defaults.")

    version = raw_data.get("version")
    if version is not None:
        if isinstance(version, int):
            data["version"] = version
        else:
            errors.append("version must be an integer")

    for field in ("default_org", "default_repo", "remote_name"):
        value = _string(raw_data.get(field), field, errors)
        if value is not None:
            data[field] = value

    canonical_path = repo_root / ".agents" / "issue-adapter.yaml"
    if adapter_path.resolve() != canonical_path.resolve():
        warnings.append(f"Adapter path is a compatibility fallback. Prefer {canonical_path}.")

    return {
        "found": True,
        "valid": not errors,
        "path": str(adapter_path),
        "data": data,
        "errors": errors,
        "warnings": warnings,
        "searched_paths": searched_paths,
    }


def main() -> int:
    cancel_timeout = SKILL_RUNTIME.arm_cli_timeout(label="issue resolve_adapter")
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    try:
        args = parser.parse_args()
        payload = load_adapter(args.repo_root.resolve())
        print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
        return 0 if payload["valid"] else 1
    finally:
        cancel_timeout()


if __name__ == "__main__":
    raise SystemExit(main())
