"""Primitive validation for file-backed Goal Run command inputs."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
ATTEMPT_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")


class GoalRunInputError(RuntimeError):
    """A typed refusal for a malformed or stale file-backed command input."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


def error(code: str, message: str) -> GoalRunInputError:
    return GoalRunInputError(code, message)


def read_json(path: Path, *, kind: str) -> tuple[dict[str, Any], str]:
    if not path.is_file():
        raise error("input-missing", f"Goal Run input file not found: {path}")
    raw = path.read_bytes()
    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise error("input-invalid", f"{path} is not canonical UTF-8 JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise error("schema-invalid", f"{path} must contain a JSON object")
    if value.get("kind") != kind:
        raise error("schema-unknown", f"{path} kind must be {kind}")
    return value, hashlib.sha256(raw).hexdigest()


def fields(value: dict[str, Any], allowed: set[str], context: str) -> None:
    extras = sorted(set(value) - allowed)
    if extras:
        raise error("schema-invalid", f"{context} contains unknown fields: {extras!r}")


def positive(value: Any, context: str) -> int:
    if type(value) is not int or value <= 0:
        raise error("identity-invalid", f"{context} must be a positive integer")
    return value


def sha(value: Any, context: str) -> str:
    if not isinstance(value, str) or not SHA256_RE.fullmatch(value):
        raise error("identity-invalid", f"{context} must be 64 lowercase hexadecimal characters")
    return value


def repo(value: Any, context: str) -> str:
    if not isinstance(value, str) or value.count("/") != 1 or not all(value.split("/")):
        raise error("identity-invalid", f"{context} must be an owner/repo identity")
    return value


def repo_file(repo_root: Path, value: Any, *, context: str, must_exist: bool = True) -> Path:
    if not isinstance(value, str) or not value.strip():
        raise error("path-invalid", f"{context} must be a repository-contained path")
    root = repo_root.resolve()
    candidate = (Path(value) if Path(value).is_absolute() else root / value).resolve()
    try:
        candidate.relative_to(root)
    except ValueError as exc:
        raise error("path-invalid", f"{context} escapes the repository root") from exc
    if must_exist and not candidate.is_file():
        raise error("input-missing", f"{context} file not found: {candidate}")
    return candidate
