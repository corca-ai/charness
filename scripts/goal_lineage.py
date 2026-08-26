#!/usr/bin/env python3
"""Validate one immutable identity record shared by goal evidence consumers.

The record separates planning provenance from execution authority.  A matching
local path or issue number is never enough: hashes and canonical repository
identities are part of the value consumed by every evidence producer.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
from pathlib import Path, PurePosixPath
from typing import Any

KIND = "charness.goal-lineage"
SCHEMA_VERSION = 1
DISPOSITIONS = frozenset({"goal-bound", "planning-only", "not-goal-bound"})
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_REPO_RE = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9_.-]*[A-Za-z0-9])?/[A-Za-z0-9](?:[A-Za-z0-9_.-]*[A-Za-z0-9])?$")
_KEY_RE = re.compile(r"^[a-z0-9][a-z0-9._-]*$")
_TOP_FIELDS = frozenset({"kind", "schema_version", "disposition", "draft", "binding", "goal_run", "work_item", "reason"})
_REFERENCE_FIELDS = frozenset({"path", "sha256"})
_ISSUE_FIELDS = frozenset({"repo", "number", "url"})
_WORK_ITEM_FIELDS = frozenset({"key", "repo", "number", "url"})


class LineageError(ValueError):
    """A typed refusal from the goal-lineage boundary."""

    def __init__(self, code: str, path: str, message: str) -> None:
        self.code = code
        self.path = path
        super().__init__(f"{code}: {path}: {message}")

    def as_dict(self) -> dict[str, str]:
        return {"code": self.code, "path": self.path, "message": str(self)}


def canonical_json_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def lineage_sha256(value: dict[str, Any]) -> str:
    """Return the digest of a validated, canonical lineage record."""
    validate_goal_lineage(value)
    return sha256_bytes(canonical_json_bytes(value))


def _fail(code: str, path: str, message: str) -> None:
    raise LineageError(code, path, message)


def _object(value: Any, path: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        _fail("lineage-invalid", path, "expected an object")
    return value


def _text(value: Any, path: str) -> str:
    if not isinstance(value, str) or not value.strip():
        _fail("lineage-invalid", path, "expected non-empty text")
    return value


def _sha(value: Any, path: str) -> str:
    candidate = _text(value, path)
    if _SHA256_RE.fullmatch(candidate) is None:
        _fail("lineage-invalid", path, "expected a lowercase SHA-256")
    return candidate


def _fields(value: dict[str, Any], expected: frozenset[str], path: str) -> None:
    missing = sorted(expected - set(value))
    extra = sorted(set(value) - expected)
    if missing or extra:
        _fail("lineage-invalid", path, f"missing={missing!r}, extra={extra!r}")


def _repo_path(value: Any, path: str) -> str:
    candidate = _text(value, path)
    pure = PurePosixPath(candidate)
    if pure.is_absolute() or "\\" in candidate or any(part in {"", ".", ".."} for part in pure.parts):
        _fail("lineage-invalid", path, "must be a canonical repository-relative path")
    return candidate


def _reference(value: Any, path: str, *, suffix: str) -> dict[str, str]:
    reference = _object(value, path)
    _fields(reference, _REFERENCE_FIELDS, path)
    relative = _repo_path(reference.get("path"), f"{path}.path")
    if not relative.endswith(suffix):
        _fail("lineage-invalid", f"{path}.path", f"must end in {suffix}")
    return {"path": relative, "sha256": _sha(reference.get("sha256"), f"{path}.sha256")}


def _issue_identity(value: Any, path: str) -> dict[str, Any]:
    identity = _object(value, path)
    _fields(identity, _ISSUE_FIELDS, path)
    repo = _text(identity.get("repo"), f"{path}.repo")
    if _REPO_RE.fullmatch(repo) is None:
        _fail("lineage-invalid", f"{path}.repo", "must be an owner/repository slug")
    number = identity.get("number")
    if type(number) is not int or number <= 0:
        _fail("lineage-invalid", f"{path}.number", "must be a positive integer")
    url = _text(identity.get("url"), f"{path}.url")
    expected = f"https://github.com/{repo}/issues/{number}"
    if url != expected:
        _fail("lineage-identity-mismatch", f"{path}.url", f"expected canonical URL {expected!r}")
    return {"repo": repo, "number": number, "url": url}


def _work_item(value: Any, path: str) -> dict[str, Any]:
    item = _object(value, path)
    _fields(item, _WORK_ITEM_FIELDS, path)
    key = _text(item.get("key"), f"{path}.key")
    if _KEY_RE.fullmatch(key) is None:
        _fail("lineage-invalid", f"{path}.key", "must be a lowercase Work Item key")
    identity = _issue_identity({key: item[key] for key in ("repo", "number", "url")}, path)
    return {"key": key, **identity}


def validate_goal_lineage(  # noqa: C901 -- all disposition and identity rules share one validated output
    value: Any,
    *,
    repo_root: Path | None = None,
    expected: dict[str, Any] | None = None,
    require_work_item: bool = False,
) -> dict[str, Any]:
    """Validate and return a copy of a complete or explicit non-bound record."""
    lineage = _object(value, "goal_lineage")
    _fields(lineage, _TOP_FIELDS, "goal_lineage")
    if lineage.get("kind") != KIND or lineage.get("schema_version") != SCHEMA_VERSION:
        _fail("lineage-schema-unknown", "goal_lineage.kind", "unsupported goal-lineage schema")
    disposition = lineage.get("disposition")
    if disposition not in DISPOSITIONS:
        _fail("lineage-invalid", "goal_lineage.disposition", "unsupported disposition")
    reason = lineage.get("reason")
    if disposition == "goal-bound":
        draft = _reference(lineage.get("draft"), "goal_lineage.draft", suffix=".md")
        binding = _reference(lineage.get("binding"), "goal_lineage.binding", suffix=".json")
        goal_run = _issue_identity(lineage.get("goal_run"), "goal_lineage.goal_run")
        if reason is not None:
            _fail("lineage-invalid", "goal_lineage.reason", "goal-bound records must not carry a refusal reason")
    elif disposition == "planning-only":
        draft = _reference(lineage.get("draft"), "goal_lineage.draft", suffix=".md")
        binding = None
        goal_run = None
        if lineage.get("binding") is not None or lineage.get("goal_run") is not None:
            _fail("lineage-authority-mismatch", "goal_lineage", "planning-only records cannot carry execution identity")
        reason = _text(reason, "goal_lineage.reason")
    else:
        draft = binding = goal_run = None
        if any(lineage.get(field) is not None for field in ("draft", "binding", "goal_run", "work_item")):
            _fail("lineage-authority-mismatch", "goal_lineage", "not-goal-bound records cannot carry goal identity")
        reason = _text(reason, "goal_lineage.reason")
    work_item = None
    if lineage.get("work_item") is not None:
        if disposition != "goal-bound":
            _fail("lineage-authority-mismatch", "goal_lineage.work_item", "work item requires goal-bound execution identity")
        work_item = _work_item(lineage["work_item"], "goal_lineage.work_item")
    elif require_work_item:
        _fail("work-item-missing", "goal_lineage.work_item", "selected evidence must name its Work Item")
    if repo_root is not None:
        root = repo_root.resolve()
        for field, reference in (("draft", draft), ("binding", binding)):
            if reference is None:
                continue
            path = root / reference["path"]
            try:
                path.resolve(strict=False).relative_to(root)
            except ValueError:
                _fail("lineage-invalid", f"goal_lineage.{field}.path", "path escapes repo root")
    result = {
        "kind": KIND,
        "schema_version": SCHEMA_VERSION,
        "disposition": disposition,
        "draft": draft,
        "binding": binding,
        "goal_run": goal_run,
        "work_item": work_item,
        "reason": reason,
    }
    if expected is not None:
        expected_value = validate_goal_lineage(expected, require_work_item=require_work_item)
        if result != expected_value:
            _fail("lineage-mismatch", "goal_lineage", "lineage identity differs from the consuming record")
    return result


def require_same_lineage(
    producer: dict[str, Any], consumer: dict[str, Any], *, require_work_item: bool = False
) -> dict[str, Any]:
    """Refuse cross-draft, cross-binding, cross-run, or cross-child substitution."""
    left = validate_goal_lineage(producer, require_work_item=require_work_item)
    right = validate_goal_lineage(consumer, require_work_item=require_work_item)
    if left != right:
        raise LineageError("lineage-mismatch", "goal_lineage", "producer and consumer identities differ")
    return right


def not_goal_bound_lineage(reason: str) -> dict[str, Any]:
    """Return the explicit identity used by evidence with no execution claim."""
    value = {
        "kind": KIND,
        "schema_version": SCHEMA_VERSION,
        "disposition": "not-goal-bound",
        "draft": None,
        "binding": None,
        "goal_run": None,
        "work_item": None,
        "reason": reason,
    }
    return validate_goal_lineage(value)


def planning_only_lineage(repo_root: Path, draft_path: Path, reason: str) -> dict[str, Any]:
    """Bind a record to draft provenance while explicitly withholding execution authority."""
    root = repo_root.resolve()
    candidate = draft_path.expanduser()
    if not candidate.is_absolute():
        candidate = root / candidate
    if candidate.is_symlink():
        raise LineageError("lineage-reference-missing", "goal_lineage.draft.path", "draft must not be a symlink")
    try:
        resolved = candidate.resolve(strict=True)
        relative = resolved.relative_to(root).as_posix()
    except (OSError, ValueError) as exc:
        raise LineageError("lineage-reference-missing", "goal_lineage.draft.path", "draft is not a file inside repo root") from exc
    if not resolved.is_file() or not relative.endswith(".md"):
        raise LineageError("lineage-reference-missing", "goal_lineage.draft.path", "draft must be a regular Markdown file inside repo root")
    value = {
        "kind": KIND,
        "schema_version": SCHEMA_VERSION,
        "disposition": "planning-only",
        "draft": {"path": relative, "sha256": sha256_bytes(resolved.read_bytes())},
        "binding": None,
        "goal_run": None,
        "work_item": None,
        "reason": reason,
    }
    return validate_goal_lineage(value, repo_root=root)


def _input_path(repo_root: Path, raw_path: Path, field: str) -> Path:
    root = repo_root.resolve()
    candidate = raw_path.expanduser()
    if not candidate.is_absolute():
        candidate = root / candidate
    try:
        relative = candidate.relative_to(root)
    except ValueError as exc:
        raise LineageError("lineage-path-invalid", field, "input must resolve inside repo root") from exc
    current = root
    for part in relative.parts:
        current /= part
        try:
            linked = os.path.lexists(current) and current.is_symlink()
        except (OSError, ValueError) as exc:
            raise LineageError("lineage-path-invalid", field, f"could not inspect input path: {exc}") from exc
        if linked:
            raise LineageError("lineage-path-invalid", field, "input must not traverse a symlink")
    try:
        resolved = candidate.resolve(strict=False)
        resolved.relative_to(root)
    except ValueError as exc:
        raise LineageError("lineage-path-invalid", field, "input must resolve inside repo root") from exc
    return resolved


def _verify_reference(repo_root: Path, reference: dict[str, str], field: str) -> None:
    path = _input_path(repo_root, Path(reference["path"]), f"goal_lineage.{field}.path")
    if not path.is_file():
        raise LineageError("lineage-reference-missing", f"goal_lineage.{field}.path", "referenced file is missing or not regular")
    actual = sha256_bytes(path.read_bytes())
    if actual != reference["sha256"]:
        raise LineageError("lineage-reference-hash-mismatch", f"goal_lineage.{field}.sha256", "referenced file hash does not match")


def verify_goal_lineage_references(repo_root: Path, value: dict[str, Any]) -> dict[str, Any]:
    """Validate a lineage value and verify the immutable draft/binding bytes."""
    root = repo_root.resolve()
    validated = validate_goal_lineage(value, repo_root=root)
    for field, reference in (("draft", validated["draft"]), ("binding", validated["binding"])):
        if reference is not None:
            _verify_reference(root, reference, field)
    return validated


def load_goal_lineage_file(
    repo_root: Path, lineage_path: Path, *, require_work_item: bool = False
) -> dict[str, Any]:
    """Load, validate, and byte-check one repo-local lineage JSON file."""
    root = repo_root.resolve()
    path = _input_path(root, lineage_path, "goal_lineage_file")
    if not path.is_file():
        raise LineageError("lineage-input-missing", "goal_lineage_file", "lineage file is missing or not regular")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise LineageError("lineage-input-invalid", "goal_lineage_file", f"cannot read valid JSON: {exc}") from exc
    validated = validate_goal_lineage(value, repo_root=root, require_work_item=require_work_item)
    return verify_goal_lineage_references(root, validated)


def require_goal_execution_identity(value: dict[str, Any]) -> dict[str, Any]:
    """Require a Work Item only when a record claims Goal Run execution.

    Planning-only and standalone evidence remain valid, but a goal-bound record
    without an exact child would otherwise look executable while carrying only
    parent-level provenance.
    """
    validated = validate_goal_lineage(value)
    if validated["disposition"] == "goal-bound" and validated["work_item"] is None:
        _fail("work-item-missing", "goal_lineage.work_item", "goal-bound execution evidence must name its Work Item")
    return validated
