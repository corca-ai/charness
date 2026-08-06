"""Compare a captured issue/tree premise before implementation begins.

The preflight is intentionally offline.  The issue adapter owns the provider
read; this module owns only coherence between that captured envelope, the
declared local tree identity, and the local decision history.
"""

from __future__ import annotations

import datetime as _datetime
import hashlib
import json
import os
import re
import subprocess
import uuid
from pathlib import Path
from typing import Any

from scripts.slice_manifest_lib import ManifestError, _safe_repo_path

SCHEMA_VERSION = 1
PREMISE_KIND = "charness.premise-preflight"
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


class PremiseError(ValueError):
    """A structured refusal or input error from the preflight."""

    def __init__(self, code: str, path: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.path = path

    def as_dict(self) -> dict[str, str]:
        return {"code": self.code, "path": self.path, "message": str(self)}


def _error(code: str, path: str, message: str) -> None:
    raise PremiseError(code, path, message)


def _mapping(value: Any, path: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        _error("invalid_premise", path, "expected an object")
    return value


def _string(value: Any, path: str) -> str:
    if not isinstance(value, str) or not value.strip():
        _error("invalid_premise", path, "expected a non-empty string")
    return value


def _integer(value: Any, path: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        _error("invalid_premise", path, "expected a non-negative integer")
    return value


def _hash(value: Any, path: str, expression: re.Pattern[str]) -> str:
    candidate = _string(value, path)
    if expression.fullmatch(candidate) is None:
        _error("invalid_premise", path, "expected a lowercase hexadecimal hash")
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


def _relative_path(value: Any, path: str) -> str:
    try:
        return _safe_repo_path(value, path)
    except ManifestError as exc:
        _error("unsafe_path", path, str(exc))
    raise AssertionError("unreachable")


def _repo_path(repo_root: Path, relative: str, path: str) -> Path:
    candidate = repo_root / relative
    try:
        resolved = candidate.resolve(strict=False)
        resolved.relative_to(repo_root.resolve())
    except ValueError:
        _error("unsafe_path", path, "path resolves outside the repository")
    return candidate


def _load_json(repo_root: Path, raw_path: Path, field: str) -> dict[str, Any]:
    try:
        relative = raw_path.resolve().relative_to(repo_root.resolve())
    except ValueError:
        _error("unsafe_path", field, "input must be inside the repository")
    if not raw_path.is_file():
        _error("missing_input", field, f"input file does not exist: `{relative}`")
    try:
        value = json.loads(raw_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        _error("invalid_json", field, f"cannot read valid JSON: {exc}")
    return _mapping(value, field)


def _git(repo_root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", *args], cwd=repo_root, capture_output=True, text=True, check=False)


def _git_bytes(repo_root: Path, *args: str) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(["git", *args], cwd=repo_root, capture_output=True, check=False)


def _index_paths(repo_root: Path) -> set[bytes]:
    result = _git_bytes(repo_root, "ls-files", "-z")
    if result.returncode != 0:
        _error("invalid_git_state", "git.index", "cannot inspect the current index")
    return {entry for entry in result.stdout.split(b"\0") if entry}


def _current_head(repo_root: Path) -> str:
    result = _git(repo_root, "rev-parse", "--verify", "HEAD^{commit}")
    if result.returncode != 0:
        _error("invalid_git_state", "tree.captured_head_sha", "repository HEAD does not resolve to a commit")
    head = result.stdout.strip()
    if _SHA_RE.fullmatch(head) is None:
        _error("invalid_git_state", "tree.captured_head_sha", "git returned an invalid commit SHA")
    return head


def _commit_exists(repo_root: Path, sha: str, path: str) -> None:
    result = _git(repo_root, "cat-file", "-e", f"{sha}^{{commit}}")
    if result.returncode != 0:
        _error("invalid_git_state", path, f"commit is not available: `{sha}`")


def _blob_bytes(repo_root: Path, revision: str, relative: str, path: str) -> bytes:
    mode_result = _git(repo_root, "ls-tree", revision, "--", relative)
    mode = mode_result.stdout.split(maxsplit=1)[0] if mode_result.returncode == 0 and mode_result.stdout.strip() else ""
    if mode not in {"100644", "100755"}:
        _error("invalid_premise", path, "protected path must be a regular non-symlink file")
    type_result = _git(repo_root, "cat-file", "-t", f"{revision}:{relative}")
    if type_result.returncode != 0 or type_result.stdout.strip() != "blob":
        _error("invalid_premise", path, "protected path must name a regular tracked blob")
    result = _git_bytes(repo_root, "show", f"{revision}:{relative}")
    if result.returncode != 0:
        _error("invalid_premise", path, "protected blob cannot be read from the captured commit")
    return result.stdout


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _canonical_json_hash(value: Any) -> str:
    rendered = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return _sha256_bytes(rendered.encode("utf-8"))


def _validate_candidate_identity(repo_root: Path, data: dict[str, Any]) -> dict[str, Any]:
    premise_id = _string(data.get("premise_id"), "premise_id")
    if _ID_RE.fullmatch(premise_id) is None:
        _error("invalid_premise", "premise_id", "must be a lowercase identifier with 3-64 characters")
    repository = _string(data.get("repository"), "repository")
    if _REPOSITORY_RE.fullmatch(repository) is None:
        _error("invalid_premise", "repository", "expected an owner/repository identifier")
    goal_path = _relative_path(data.get("goal_path"), "goal_path")
    if not _repo_path(repo_root, goal_path, "goal_path").is_file():
        _error("invalid_premise", "goal_path", "goal binding must name an existing file")
    slice_id = _string(data.get("slice_id"), "slice_id")
    if _ID_RE.fullmatch(slice_id) is None:
        _error("invalid_premise", "slice_id", "must be a lowercase identifier with 3-64 characters")
    issue = _mapping(data.get("issue"), "issue")
    number = _integer(issue.get("number"), "issue.number")
    if number < 1:
        _error("invalid_premise", "issue.number", "issue number must be positive")
    if issue.get("expected_state") != "OPEN":
        _error("invalid_premise", "issue.expected_state", "premise expected_state must be `OPEN`")
    captured = _mapping(issue.get("captured"), "issue.captured")
    _hash(captured.get("body_sha256"), "issue.captured.body_sha256", _SHA256_RE)
    _hash(captured.get("comments_sha256"), "issue.captured.comments_sha256", _SHA256_RE)
    _integer(captured.get("comment_count"), "issue.captured.comment_count")
    _timestamp(captured.get("updated_at"), "issue.captured.updated_at")
    return {"premise_id": premise_id, "repository": repository, "goal_path": goal_path, "slice_id": slice_id, "issue_number": number, "captured_issue": captured}


def _validate_candidate_tree(repo_root: Path, tree: dict[str, Any]) -> dict[str, Any]:
    captured_head = _hash(tree.get("captured_head_sha"), "tree.captured_head_sha", _SHA_RE)
    _commit_exists(repo_root, captured_head, "tree.captured_head_sha")
    protected = tree.get("protected")
    if not isinstance(protected, list) or not protected:
        _error("invalid_premise", "tree.protected", "declare at least one protected path")
    seen: set[str] = set()
    protected_rows: list[dict[str, str]] = []
    for index, raw in enumerate(protected):
        row = _mapping(raw, f"tree.protected[{index}]")
        relative = _relative_path(row.get("path"), f"tree.protected[{index}].path")
        if relative in seen:
            _error("invalid_premise", f"tree.protected[{index}].path", f"duplicate protected path `{relative}`")
        seen.add(relative)
        digest = _hash(row.get("sha256"), f"tree.protected[{index}].sha256", _SHA256_RE)
        actual = _sha256_bytes(_blob_bytes(repo_root, captured_head, relative, f"tree.protected[{index}].path"))
        if digest != actual:
            _error("invalid_premise", f"tree.protected[{index}].sha256", "hash does not match captured HEAD blob")
        protected_rows.append({"path": relative, "sha256": digest})
    expected_missing = tree.get("expected_missing", [])
    if not isinstance(expected_missing, list):
        _error("invalid_premise", "tree.expected_missing", "expected an array of paths")
    missing_rows: list[str] = []
    for index, raw in enumerate(expected_missing):
        relative = _relative_path(raw, f"tree.expected_missing[{index}]")
        if relative in seen:
            _error("invalid_premise", f"tree.expected_missing[{index}]", "path overlaps protected paths")
        if relative in missing_rows:
            _error("invalid_premise", f"tree.expected_missing[{index}]", f"duplicate expected-missing path `{relative}`")
        missing_rows.append(relative)
        if _git(repo_root, "cat-file", "-e", f"{captured_head}:{relative}").returncode == 0:
            _error("invalid_premise", f"tree.expected_missing[{index}]", "path exists at captured HEAD")
    return {"captured_head_sha": captured_head, "protected": protected_rows, "expected_missing": missing_rows}


def _validate_candidate(repo_root: Path, data: dict[str, Any]) -> dict[str, Any]:
    if data.get("kind") != PREMISE_KIND or data.get("schema_version") != SCHEMA_VERSION:
        _error("invalid_premise", "kind", f"expected `{PREMISE_KIND}` schema version {SCHEMA_VERSION}")
    identity = _validate_candidate_identity(repo_root, data)
    tree = _validate_candidate_tree(repo_root, _mapping(data.get("tree"), "tree"))
    decision_log = _relative_path(data.get("decision_log"), "decision_log")
    return {**identity, **tree, "decision_log": decision_log}


def _validate_issue(repo_root: Path, data: dict[str, Any], candidate: dict[str, Any]) -> dict[str, Any]:
    if data.get("ok") is not True or data.get("comments_read") is not True:
        _error("invalid_issue_readback", "issue_readback", "readback must have `ok: true` and `comments_read: true`")
    repository = data.get("repo")
    if repository != candidate["repository"]:
        _error("invalid_issue_readback", "repo", "readback repository does not match premise repository")
    if data.get("number") != candidate["issue_number"]:
        _error("invalid_issue_readback", "number", "readback issue number does not match premise")
    issue = data.get("issue")
    if not isinstance(issue, dict):
        _error("invalid_issue_readback", "issue", "readback must contain an issue object")
    if isinstance(data.get("number"), bool) or not isinstance(data.get("number"), int):
        _error("invalid_issue_readback", "number", "outer issue number must be an integer")
    if isinstance(issue.get("number"), bool) or not isinstance(issue.get("number"), int):
        _error("invalid_issue_readback", "issue.number", "nested issue number must be an integer")
    if issue.get("number") != data.get("number"):
        _error("invalid_issue_readback", "issue.number", "nested issue number disagrees with outer number")
    if issue.get("body") is not None and not isinstance(issue.get("body"), str):
        _error("invalid_issue_readback", "issue.body", "issue body must be a string or null")
    if not isinstance(issue.get("body"), str):
        _error("invalid_issue_readback", "issue.body", "issue body is required for premise identity")
    comments = issue.get("comments")
    if not isinstance(comments, list) or not isinstance(data.get("comment_count"), int) or isinstance(data.get("comment_count"), bool):
        _error("invalid_issue_readback", "issue.comments", "comments must be a list with an integer outer count")
    if data["comment_count"] != len(comments):
        _error("invalid_issue_readback", "comment_count", "outer comment count does not match comments list")
    state = issue.get("state")
    if not isinstance(state, str) or state.strip().upper() not in _STATES:
        _error("invalid_issue_readback", "issue.state", "issue state must be OPEN or CLOSED")
    updated_at = issue.get("updatedAt")
    _timestamp(updated_at, "issue.updatedAt", error_code="invalid_issue_readback")
    return {
        "repository": repository,
        "number": data["number"],
        "state": state.strip().upper(),
        "body_sha256": _sha256_bytes(issue["body"].encode("utf-8")),
        "comments_sha256": _canonical_json_hash(comments),
        "comment_count": len(comments),
        "updated_at": updated_at,
    }


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
    except ManifestError as exc:
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


def _marker_seen(repo_root: Path, premise_id: str) -> bool:
    result = _git(repo_root, "log", "HEAD", "--format=%B")
    if result.returncode != 0:
        _error("invalid_git_state", "git.log", "cannot inspect commit history from current HEAD")
    marker = f"Charness-Premise-ID: {premise_id}"
    return any(line == marker for line in result.stdout.splitlines())


def _protected_observations(repo_root: Path, candidate: dict[str, Any]) -> tuple[dict[str, list[dict[str, Any]]], bool]:
    observations: dict[str, list[dict[str, Any]]] = {"protected": [], "expected_missing": []}
    drift = False
    for row in candidate["protected"]:
        path = _repo_path(repo_root, row["path"], f"tree.protected[{row['path']}]")
        worktree_sha: str | None = None
        index_sha: str | None = None
        if path.is_symlink() or not path.is_file():
            drift = True
        else:
            try:
                worktree_sha = _sha256_bytes(path.read_bytes())
            except OSError:
                drift = True
            else:
                drift = drift or worktree_sha != row["sha256"]
        index = _git_bytes(repo_root, "show", f":{row['path']}")
        if index.returncode == 0:
            index_sha = _sha256_bytes(index.stdout)
        if index_sha != row["sha256"]:
            drift = True
        observations["protected"].append({"path": row["path"], "captured_sha256": row["sha256"], "index_sha256": index_sha, "worktree_sha256": worktree_sha})
    index_paths = _index_paths(repo_root)
    for relative in candidate["expected_missing"]:
        path = _repo_path(repo_root, relative, "tree.expected_missing")
        worktree_present = os.path.lexists(path)
        relative_bytes = relative.encode("utf-8")
        index_present = any(
            indexed == relative_bytes or indexed.startswith(relative_bytes + b"/")
            for indexed in index_paths
        )
        if worktree_present or index_present:
            drift = True
        observations["expected_missing"].append({"path": relative, "expected_absent": True, "index_present": index_present, "worktree_present": worktree_present})
    return observations, drift


def _record(repo_root: Path, candidate: dict[str, Any], issue: dict[str, Any], current_head: str, observations: dict[str, list[dict[str, Any]]], reasons: list[dict[str, str]], *, status: str) -> dict[str, Any]:
    attempt_id = uuid.uuid4().hex
    return {
        "kind": DECISION_KIND,
        "schema_version": SCHEMA_VERSION,
        "recorded_at": _datetime.datetime.now(_datetime.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "attempt_id": attempt_id,
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


def run_preflight(repo_root: Path, premise_path: Path, issue_path: Path, *, decision_log: str | None = None) -> dict[str, Any]:
    candidate = _validate_candidate(repo_root, _load_json(repo_root, premise_path, "premise"))
    issue = _validate_issue(repo_root, _load_json(repo_root, issue_path, "issue_readback"), candidate)
    records = _read_decisions(repo_root, decision_log or candidate["decision_log"])
    current_head = _current_head(repo_root)
    observations: dict[str, list[dict[str, Any]]] = {"protected": [], "expected_missing": []}
    reasons: list[dict[str, str]] = []
    if issue["state"] == "CLOSED" or _marker_seen(repo_root, candidate["premise_id"]):
        reasons.append({"code": "already_shipped", "path": "issue.state", "message": "issue is closed or the exact premise marker is already reachable from current HEAD"})
    if any(record.get("status") == "accepted" and record.get("premise_id") == candidate["premise_id"] for record in records):
        reasons.append({"code": "duplicate_premise", "path": "decision_log", "message": "an accepted decision already exists for this premise ID"})
    captured = candidate["captured_issue"]
    if issue["state"] != "CLOSED" and any(issue[key] != captured[key] for key in ("body_sha256", "comments_sha256", "comment_count", "updated_at")):
        reasons.append({"code": "stale_issue", "path": "issue_readback", "message": "captured issue identity does not match the readback"})
    if current_head != candidate["captured_head_sha"]:
        reasons.append({"code": "stale_tree", "path": "tree.captured_head_sha", "message": "current HEAD moved after the premise was captured"})
    else:
        observations, drift = _protected_observations(repo_root, candidate)
        if drift:
            reasons.append({"code": "partial_repair", "path": "tree.protected", "message": "protected index/worktree or expected-missing paths changed before implementation"})
    reasons.sort(key=lambda item: REASON_ORDER.index(item["code"]))
    status = "accepted" if not reasons else "refused"
    record = _record(repo_root, candidate, issue, current_head, observations, reasons, status=status)
    log_path = decision_log or candidate["decision_log"]
    log_path = _relative_path(log_path, "decision_log")
    _append_decision(repo_root, log_path, record)
    return {"status": status, "exit_code": 0 if status == "accepted" else 1, "persisted": True, "decision_log": log_path, "decision": record, "non_claim": NON_CLAIM}
