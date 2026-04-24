from __future__ import annotations

import os
from pathlib import Path
from typing import Any


def repo_relative_path(repo_root: Path, path: Path) -> str:
    return path.resolve().relative_to(repo_root.resolve()).as_posix()


def portable_path_value(repo_root: Path, value: str | Path, *, external_label: str = "external-path") -> str:
    path = Path(value)
    if not path.is_absolute():
        return path.as_posix()
    try:
        return repo_relative_path(repo_root, path)
    except ValueError:
        return f"{external_label}:{path.name}"


def portable_path_provenance(repo_root: Path, value: str | Path) -> dict[str, str]:
    path = Path(value)
    if not path.is_absolute():
        return {"kind": "repo-relative"}
    try:
        repo_relative_path(repo_root, path)
    except ValueError:
        return {"kind": "external-path", "basename": path.name}
    return {"kind": "repo-root-relative"}


def sanitize_artifact_json(value: Any, *, repo_root: Path) -> Any:
    if isinstance(value, dict):
        return {key: _sanitize_mapping_value(key, item, repo_root=repo_root) for key, item in value.items()}
    if isinstance(value, list):
        return [sanitize_artifact_json(item, repo_root=repo_root) for item in value]
    return value


def _sanitize_mapping_value(key: str, value: Any, *, repo_root: Path) -> Any:
    key_lower = key.lower()
    if isinstance(value, str) and _looks_path_key(key_lower):
        return portable_path_value(repo_root, value)
    if isinstance(value, list) and _looks_path_key(key_lower):
        return [
            portable_path_value(repo_root, item) if isinstance(item, str) else sanitize_artifact_json(item, repo_root=repo_root)
            for item in value
        ]
    return sanitize_artifact_json(value, repo_root=repo_root)


def _looks_path_key(key: str) -> bool:
    return key == "path" or key.endswith("path") or key.endswith("paths") or "path_" in key


def sanitize_diagnostic_text(text: str, *, repo_root: Path) -> str:
    if not text:
        return text
    repo_text = str(repo_root.resolve())
    home_text = str(Path.home())
    sanitized = text.replace(repo_text, ".")
    if home_text and home_text != os.sep:
        sanitized = sanitized.replace(home_text, "$HOME")
    return sanitized
