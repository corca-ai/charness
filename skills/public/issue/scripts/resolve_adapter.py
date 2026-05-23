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


FEATURE_BRIEF_PAUSE_VALUES = ("on-open-decisions", "always", "never")
DEFAULT_FEATURE_BRIEF_PAUSE = "on-open-decisions"


def infer_defaults() -> dict[str, Any]:
    return {
        "version": 1,
        "default_org": "corca-ai",
        "default_repo": None,
        "remote_name": "origin",
        "issue_backend": default_backend(),
        "feature_brief_pause": DEFAULT_FEATURE_BRIEF_PAUSE,
    }


def default_backend() -> dict[str, Any]:
    return {"id": "gh", "binary": "gh", "commands": None}


def _parse_feature_brief_pause(raw: Any, errors: list[str]) -> str:
    if raw is None:
        return DEFAULT_FEATURE_BRIEF_PAUSE
    if not isinstance(raw, str) or raw not in FEATURE_BRIEF_PAUSE_VALUES:
        errors.append(
            "feature_brief_pause must be one of: "
            + ", ".join(FEATURE_BRIEF_PAUSE_VALUES)
        )
        return DEFAULT_FEATURE_BRIEF_PAUSE
    return raw


def _string(value: Any, field: str, errors: list[str]) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{field} must be a non-empty string")
        return None
    return value


def _parse_backend(raw: Any, errors: list[str], warnings: list[str]) -> dict[str, Any]:
    if raw is None:
        return default_backend()
    if not isinstance(raw, dict):
        errors.append("issue_backend must be a mapping")
        return default_backend()
    backend_id = _string(raw.get("id"), "issue_backend.id", errors) or "gh"
    binary = _string(raw.get("binary"), "issue_backend.binary", errors) or backend_id
    commands: dict[str, list[str]] | None = None
    raw_commands = raw.get("commands")
    if raw_commands is not None:
        if not isinstance(raw_commands, dict):
            errors.append("issue_backend.commands must be a mapping")
        else:
            commands = {}
            for op, argv in raw_commands.items():
                if not isinstance(argv, list) or not all(isinstance(part, str) for part in argv):
                    errors.append(f"issue_backend.commands.{op} must be a list of strings")
                    continue
                commands[op] = list(argv)
    if backend_id != "gh" and not commands:
        warnings.append(
            f"issue_backend.id={backend_id} declared without commands; "
            "agent must follow the host-documented command shape until commands templates are filled in"
        )
    return {"id": backend_id, "binary": binary, "commands": commands}


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

    data["issue_backend"] = _parse_backend(raw_data.get("issue_backend"), errors, warnings)
    data["feature_brief_pause"] = _parse_feature_brief_pause(
        raw_data.get("feature_brief_pause"), errors
    )

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
    parser.add_argument("--repo-root", type=Path, default=Path.cwd(), help="Repo root used to locate the issue adapter")
    try:
        args = parser.parse_args()
        payload = load_adapter(args.repo_root.resolve())
        print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
        return 0 if payload["valid"] else 1
    finally:
        cancel_timeout()


if __name__ == "__main__":
    raise SystemExit(main())
