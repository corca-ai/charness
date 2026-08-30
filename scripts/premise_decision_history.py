"""Decision-history contract and persistence for premise preflight."""

from __future__ import annotations

import datetime as _datetime
import json
import os
import re
import uuid
from pathlib import Path, PurePosixPath
from typing import Any

SCHEMA_VERSION = 1
DECISION_KIND = "charness.premise-decision"
REASON_ORDER = (
    "already_shipped",
    "duplicate_premise",
    "stale_issue",
    "stale_tree",
    "partial_repair",
)
NON_CLAIM = (
    "offline captured-readback coherence only; provider freshness, issue writes, "
    "runtime behavior, installed-consumer behavior, and remote CI are not claimed"
)
_ID_RE = re.compile(r"^[a-z0-9][a-z0-9._-]{2,63}$")
_REPOSITORY_RE = re.compile(r"^[^/\s]+/[^/\s]+$")
_SHA_RE = re.compile(r"^[0-9a-f]{40}$")
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_RFC3339_UTC_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z$")
_STATES = frozenset({"OPEN", "CLOSED"})


class PremisePathError(ValueError):
    """A premise contains an unsafe repo-relative path."""


class PremiseError(ValueError):
    """A structured refusal or input error from the premise contract."""

    def __init__(self, code: str, path: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.path = path

    def as_dict(self) -> dict[str, str]:
        return {"code": self.code, "path": self.path, "message": str(self)}


def _error(code: str, path: str, message: str) -> None:
    raise PremiseError(code, path, message)


def _safe_repo_path(value: Any, path: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise PremisePathError(f"{path}: expected a non-empty string")
    if "\\" in value:
        raise PremisePathError("use a repo-relative POSIX path, not a backslash path")
    parsed = PurePosixPath(value)
    if parsed.is_absolute() or ".." in parsed.parts or "." in parsed.parts:
        raise PremisePathError("path must be relative and must not contain `.` or `..`")
    if value.endswith("/"):
        raise PremisePathError("path must not have a trailing slash")
    return value


def _repo_path(repo_root: Path, relative: str, path: str) -> Path:
    candidate = repo_root / relative
    try:
        resolved = candidate.resolve(strict=False)
        resolved.relative_to(repo_root.resolve())
    except ValueError:
        _error("unsafe_path", path, "path resolves outside the repository")
    return candidate


def _timestamp(value: Any, path: str, *, error_code: str = "invalid_premise") -> str:
    if not isinstance(value, str) or not value.strip():
        _error(error_code, path, "expected a non-empty timestamp")
    candidate = value
    if _RFC3339_UTC_RE.fullmatch(candidate) is None:
        _error(error_code, path, "expected an RFC3339 UTC timestamp ending in `Z`")
    try:
        parsed = _datetime.datetime.fromisoformat(candidate[:-1] + "+00:00")
    except ValueError as exc:
        _error(error_code, path, f"invalid RFC3339 timestamp: {exc}")
    if parsed.tzinfo is None:
        _error(error_code, path, "timestamp must include a UTC offset")
    return candidate


def _history_string(value: Any, path: str) -> str:
    if not isinstance(value, str) or not value.strip():
        _error("invalid_decision_history", path, "expected a non-empty string")
    return value


def _history_hash(value: Any, path: str) -> str:
    candidate = _history_string(value, path)
    if _SHA256_RE.fullmatch(candidate) is None:
        _error("invalid_decision_history", path, "expected a lowercase SHA-256 hash")
    return candidate


def _history_git_sha(value: Any, path: str) -> str:
    candidate = _history_string(value, path)
    if _SHA_RE.fullmatch(candidate) is None:
        _error("invalid_decision_history", path, "expected a lowercase Git commit SHA")
    return candidate


def _history_path(value: Any, path: str) -> str:
    try:
        return _safe_repo_path(value, path)
    except PremisePathError as exc:
        _error("invalid_decision_history", path, str(exc))
    raise AssertionError("unreachable")


def _history_observation(record: dict[str, Any], path: str) -> None:
    issue = record.get("issue_observation")
    if not isinstance(issue, dict):
        _error("invalid_decision_history", f"{path}.issue_observation", "issue observation is required")
    if not isinstance(issue.get("number"), int) or isinstance(issue.get("number"), bool) or issue["number"] < 1:
        _error("invalid_decision_history", f"{path}.issue_observation.number", "issue number is invalid")
    if issue.get("state") not in _STATES:
        _error("invalid_decision_history", f"{path}.issue_observation.state", "issue state is invalid")
    _history_string(issue.get("repository"), f"{path}.issue_observation.repository")
    _history_hash(issue.get("body_sha256"), f"{path}.issue_observation.body_sha256")
    _history_hash(issue.get("comments_sha256"), f"{path}.issue_observation.comments_sha256")
    if not isinstance(issue.get("comment_count"), int) or isinstance(issue.get("comment_count"), bool):
        _error("invalid_decision_history", f"{path}.issue_observation.comment_count", "comment count is invalid")
    _timestamp(issue.get("updated_at"), f"{path}.issue_observation.updated_at", error_code="invalid_decision_history")
    tree = record.get("tree_observation")
    if not isinstance(tree, dict):
        _error("invalid_decision_history", f"{path}.tree_observation", "tree observation is required")
    _history_git_sha(tree.get("captured_head_sha"), f"{path}.tree_observation.captured_head_sha")
    _history_git_sha(tree.get("current_head_sha"), f"{path}.tree_observation.current_head_sha")
    for field in ("protected", "expected_missing"):
        if not isinstance(tree.get(field), list):
            _error("invalid_decision_history", f"{path}.tree_observation.{field}", "observation list is required")
    for index, row in enumerate(tree["protected"]):
        if not isinstance(row, dict):
            _error("invalid_decision_history", f"{path}.tree_observation.protected[{index}]", "observation must be an object")
        _history_path(row.get("path"), f"{path}.tree_observation.protected[{index}].path")
        _history_hash(row.get("captured_sha256"), f"{path}.tree_observation.protected[{index}].captured_sha256")
        for field in ("index_sha256", "worktree_sha256"):
            value = row.get(field)
            if value is not None:
                _history_hash(value, f"{path}.tree_observation.protected[{index}].{field}")
    for index, row in enumerate(tree["expected_missing"]):
        if not isinstance(row, dict):
            _error("invalid_decision_history", f"{path}.tree_observation.expected_missing[{index}]", "observation must be an object")
        _history_path(row.get("path"), f"{path}.tree_observation.expected_missing[{index}].path")
        if row.get("expected_absent") is not True or not isinstance(row.get("index_present"), bool) or not isinstance(row.get("worktree_present"), bool):
            _error("invalid_decision_history", f"{path}.tree_observation.expected_missing[{index}]", "missing-path observation is incomplete")


def _validate_decision_record(repo_root: Path, record: Any, index: int) -> dict[str, Any]:
    del repo_root
    path = f"decision_log[{index}]"
    if not isinstance(record, dict):
        _error("invalid_decision_history", path, "record must be an object")
    if record.get("kind") != DECISION_KIND or record.get("schema_version") != SCHEMA_VERSION:
        _error("invalid_decision_history", path, "record kind or schema version is invalid")
    status = record.get("status")
    if status not in {"accepted", "refused"}:
        _error("invalid_decision_history", f"{path}.status", "record status is invalid")
    premise_id = _history_string(record.get("premise_id"), f"{path}.premise_id")
    if _ID_RE.fullmatch(premise_id) is None:
        _error("invalid_decision_history", f"{path}.premise_id", "record premise ID is invalid")
    attempt_id = _history_string(record.get("attempt_id"), f"{path}.attempt_id")
    if re.fullmatch(r"[0-9a-f]{32}", attempt_id) is None:
        _error("invalid_decision_history", f"{path}.attempt_id", "record attempt ID is invalid")
    repository = _history_string(record.get("repository"), f"{path}.repository")
    if _REPOSITORY_RE.fullmatch(repository) is None:
        _error("invalid_decision_history", f"{path}.repository", "record repository is invalid")
    _history_path(record.get("goal_path"), f"{path}.goal_path")
    slice_id = _history_string(record.get("slice_id"), f"{path}.slice_id")
    if _ID_RE.fullmatch(slice_id) is None:
        _error("invalid_decision_history", f"{path}.slice_id", "record slice ID is invalid")
    _timestamp(record.get("recorded_at"), f"{path}.recorded_at", error_code="invalid_decision_history")
    reason_codes = record.get("reason_codes")
    reasons = record.get("reasons")
    if not isinstance(reason_codes, list) or not all(isinstance(code, str) and code in REASON_ORDER for code in reason_codes):
        _error("invalid_decision_history", f"{path}.reason_codes", "record reason codes are invalid")
    if len(set(reason_codes)) != len(reason_codes) or reason_codes != sorted(reason_codes, key=REASON_ORDER.index):
        _error("invalid_decision_history", f"{path}.reason_codes", "record reason codes are not unique and ordered")
    if not isinstance(reasons, list) or len(reasons) != len(reason_codes):
        _error("invalid_decision_history", f"{path}.reasons", "record reasons do not match reason codes")
    for reason_index, reason in enumerate(reasons):
        if not isinstance(reason, dict) or reason.get("code") != reason_codes[reason_index]:
            _error("invalid_decision_history", f"{path}.reasons[{reason_index}]", "record reason is incomplete")
        _history_string(reason.get("path"), f"{path}.reasons[{reason_index}].path")
        _history_string(reason.get("message"), f"{path}.reasons[{reason_index}].message")
    if (status == "accepted") != (not reason_codes):
        _error("invalid_decision_history", f"{path}.status", "accepted/refused status disagrees with reasons")
    if record.get("non_claim") != NON_CLAIM:
        _error("invalid_decision_history", f"{path}.non_claim", "record non-claim is missing or changed")
    _history_observation(record, path)
    return record


def _read_decisions(repo_root: Path, relative: str) -> list[dict[str, Any]]:
    path = _repo_path(repo_root, relative, "decision_log")
    if path.is_symlink():
        _error("invalid_decision_history", "decision_log", "decision log must not be a symlink")
    if not path.exists():
        return []
    if not path.is_file():
        _error("invalid_decision_history", "decision_log", "decision log is not a regular file")
    records: list[dict[str, Any]] = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as exc:
        _error("invalid_decision_history", "decision_log", f"cannot read decision log: {exc}")
    for index, line in enumerate(lines, start=1):
        if not line.strip():
            _error("invalid_decision_history", f"decision_log[{index}]", "blank JSONL records are not allowed")
        try:
            record = json.loads(line)
        except json.JSONDecodeError as exc:
            _error("invalid_decision_history", f"decision_log[{index}]", f"invalid JSON: {exc.msg}")
        records.append(_validate_decision_record(repo_root, record, index))
    return records


def _record(
    repo_root: Path,
    candidate: dict[str, Any],
    issue: dict[str, Any],
    current_head: str,
    observations: dict[str, list[dict[str, Any]]],
    reasons: list[dict[str, str]],
    *,
    status: str,
) -> dict[str, Any]:
    del repo_root
    return {
        "kind": DECISION_KIND,
        "schema_version": SCHEMA_VERSION,
        "recorded_at": _datetime.datetime.now(_datetime.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "attempt_id": uuid.uuid4().hex,
        "premise_id": candidate["premise_id"],
        "repository": candidate["repository"],
        "goal_path": candidate["goal_path"],
        "slice_id": candidate["slice_id"],
        "status": status,
        "reason_codes": [item["code"] for item in reasons],
        "reasons": reasons,
        "issue_observation": issue,
        "tree_observation": {"captured_head_sha": candidate["captured_head_sha"], "current_head_sha": current_head, **observations},
        "non_claim": NON_CLAIM,
    }


def _append_decision(repo_root: Path, relative: str, record: dict[str, Any]) -> None:
    path = _repo_path(repo_root, relative, "decision_log")
    if path.is_symlink():
        _error("decision_log_write_failed", "decision_log", "decision log must not be a symlink")
    if os.path.lexists(path) and not path.is_file():
        _error("decision_log_write_failed", "decision_log", "decision log must be a regular file")
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n")
    except OSError as exc:
        _error("decision_log_write_failed", "decision_log", f"cannot append decision: {exc}")
