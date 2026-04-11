#!/usr/bin/env python3
# ruff: noqa: E402
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


def _runtime_root() -> Path:
    script_path = Path(__file__).resolve()
    for ancestor in script_path.parents:
        if (ancestor / "scripts" / "adapter_lib.py").is_file():
            return ancestor
    return script_path.parents[4]


REPO_ROOT = _runtime_root()
sys.path.insert(0, str(REPO_ROOT))

from scripts.adapter_lib import load_yaml_file

ADAPTER_CANDIDATES = (
    Path(".agents/narrative-adapter.yaml"),
    Path(".codex/narrative-adapter.yaml"),
    Path(".claude/narrative-adapter.yaml"),
    Path("docs/narrative-adapter.yaml"),
    Path("narrative-adapter.yaml"),
)

STRING_FIELDS = ("repo", "language", "output_dir", "preset_id", "preset_version", "customized_from", "remote_name")
LIST_FIELDS = ("source_documents", "mutable_documents")
ARTIFACT_FILENAME = "narrative.md"


def _string(value: Any, field: str, errors: list[str]) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        errors.append(f"{field} must be a string")
        return None
    return value


def _string_list(value: Any, field: str, errors: list[str]) -> list[str] | None:
    if value is None:
        return None
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        errors.append(f"{field} must be a list of strings")
        return None
    return list(value)


def _infer_source_documents(repo_root: Path) -> list[str]:
    candidates = [
        "README.md",
        "docs/roadmap.md",
        "docs/decisions.md",
        "docs/operator-acceptance.md",
        "docs/handoff.md",
    ]
    inferred = [path for path in candidates if (repo_root / path).is_file()]
    return inferred or ["README.md"]


def infer_repo_defaults(repo_root: Path) -> dict[str, Any]:
    inferred_docs = _infer_source_documents(repo_root)
    return {
        "version": 1,
        "repo": repo_root.name,
        "language": "en",
        "output_dir": "skill-outputs/narrative",
        "source_documents": inferred_docs,
        "mutable_documents": inferred_docs,
        "remote_name": "origin",
    }


def validate_adapter_data(data: dict[str, Any], repo_root: Path) -> tuple[dict[str, Any], list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    validated = infer_repo_defaults(repo_root)

    version = data.get("version")
    if version is not None:
        if isinstance(version, int):
            validated["version"] = version
        else:
            errors.append("version must be an integer")

    for field in STRING_FIELDS:
        value = _string(data.get(field), field, errors)
        if value is not None:
            validated[field] = value

    for field in LIST_FIELDS:
        value = _string_list(data.get(field), field, errors)
        if value is not None:
            validated[field] = value

    if data.get("repo") == "CHANGE_ME":
        warnings.append("repo is still set to CHANGE_ME")
    if not validated["source_documents"]:
        errors.append("source_documents must not be empty")
    if not validated["mutable_documents"]:
        errors.append("mutable_documents must not be empty")

    return validated, errors, warnings


def find_adapter(repo_root: Path) -> Path | None:
    for candidate in ADAPTER_CANDIDATES:
        path = repo_root / candidate
        if path.is_file():
            return path
    return None


def _artifact_path(output_dir: str) -> str:
    return str(Path(output_dir) / ARTIFACT_FILENAME)


def load_adapter(repo_root: Path) -> dict[str, Any]:
    searched_paths = [str((repo_root / candidate).resolve()) for candidate in ADAPTER_CANDIDATES]
    adapter_path = find_adapter(repo_root)
    if adapter_path is None:
        data = infer_repo_defaults(repo_root)
        return {
            "found": False,
            "valid": True,
            "path": None,
            "data": data,
            "artifact_filename": ARTIFACT_FILENAME,
            "artifact_path": _artifact_path(data["output_dir"]),
            "errors": [],
            "warnings": [
                "No narrative adapter found. Using inferred source-of-truth defaults.",
                "Create .agents/narrative-adapter.yaml to pin the truth surface and mutable documents.",
            ],
            "searched_paths": searched_paths,
        }

    raw = load_yaml_file(adapter_path)
    raw_data = raw if isinstance(raw, dict) else {}
    warnings: list[str] = []
    canonical_path = repo_root / ".agents" / "narrative-adapter.yaml"
    if not isinstance(raw, dict):
        warnings.append("Adapter file did not contain a mapping. Using inferred defaults.")
    if adapter_path.resolve() != canonical_path.resolve():
        warnings.append(f"Adapter path is a compatibility fallback. Prefer {canonical_path}.")
    data, errors, extra_warnings = validate_adapter_data(raw_data, repo_root)
    warnings.extend(extra_warnings)
    return {
        "found": True,
        "valid": not errors,
        "path": str(adapter_path),
        "data": data,
        "artifact_filename": ARTIFACT_FILENAME,
        "artifact_path": _artifact_path(data["output_dir"]),
        "errors": errors,
        "warnings": warnings,
        "searched_paths": searched_paths,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    args = parser.parse_args()
    sys.stdout.write(
        json.dumps(load_adapter(args.repo_root.resolve()), ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    )


if __name__ == "__main__":
    main()
