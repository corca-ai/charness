"""Compare a captured issue/tree premise before implementation begins.

The preflight is intentionally offline.  The issue adapter owns the provider
read; this module owns only coherence between that captured envelope, the
declared local tree identity, and the local decision history.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any


def _load_repo_runtime_bootstrap():
    pathlib, sys = __import__("pathlib"), __import__("sys")
    marker = ("scripts", "adapter_lib.py")
    parents = pathlib.Path(__file__).resolve().parents
    root = next((p for p in parents if p.joinpath(*marker).is_file()), None)
    if root is None:
        raise ImportError("scripts/adapter_lib.py not found above " + __file__)
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))


_load_repo_runtime_bootstrap()

from scripts.premise.premise_decision_history import (  # noqa: E402
    _ID_RE,
    _REPOSITORY_RE,
    _SHA256_RE,
    _SHA_RE,
    _STATES,
    NON_CLAIM,
    REASON_ORDER,
    SCHEMA_VERSION,
    PremiseError,
    PremisePathError,
    _append_decision,
    _error,
    _read_decisions,
    _record,
    _repo_path,
    _safe_repo_path,
    _timestamp,
)
from scripts.premise.premise_git_snapshot import (  # noqa: E402
    CapturedTreeSnapshot,
    history_contains_exact_line,
    inspect_captured_tree,
)
from scripts.premise.premise_tree_observation import (  # noqa: E402
    CurrentTreeInspectionError,
    ObservationPathEscape,
    observe_current_tree,
)

__all__ = ["PremiseError", "run_preflight"]

PREMISE_KIND = "charness.premise-preflight"


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


def _relative_path(value: Any, path: str) -> str:
    try:
        return _safe_repo_path(value, path)
    except PremisePathError as exc:
        _error("unsafe_path", path, str(exc))
    raise AssertionError("unreachable")


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
    snapshot = inspect_captured_tree(
        repo_root,
        captured_head,
        [row["path"] for row in protected_rows],
        missing_rows,
    )
    if not snapshot.available or not snapshot.commit_exists:
        _error(
            "invalid_git_state",
            "tree.captured_head_sha",
            f"commit is not available: `{captured_head}`",
        )
    for index, row in enumerate(protected_rows):
        path = row["path"]
        if snapshot.modes.get(path) not in {"100644", "100755"}:
            _error(
                "invalid_premise",
                f"tree.protected[{index}].path",
                "protected path must be a regular non-symlink file",
            )
        git_object = snapshot.objects.get(path)
        if git_object is None or git_object[0] != "blob":
            _error(
                "invalid_premise",
                f"tree.protected[{index}].path",
                "protected path must name a regular tracked blob",
            )
        if row["sha256"] != _sha256_bytes(git_object[1]):
            _error(
                "invalid_premise",
                f"tree.protected[{index}].sha256",
                "hash does not match captured HEAD blob",
            )
    for index, relative in enumerate(missing_rows):
        if snapshot.objects.get(relative) is not None:
            _error("invalid_premise", f"tree.expected_missing[{index}]", "path exists at captured HEAD")
    return {
        "captured_head_sha": captured_head,
        "protected": protected_rows,
        "expected_missing": missing_rows,
        "snapshot": snapshot,
    }


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


def _marker_seen(repo_root: Path, premise_id: str, snapshot: CapturedTreeSnapshot) -> bool:
    if snapshot.current_head_sha is None or snapshot.current_head_commit is None:
        _error("invalid_git_state", "git.log", "cannot inspect commit history from current HEAD")
    found = history_contains_exact_line(
        repo_root,
        snapshot.current_head_sha,
        snapshot.current_head_commit,
        f"Charness-Premise-ID: {premise_id}",
    )
    if found is None:
        _error("invalid_git_state", "git.log", "cannot inspect commit history from current HEAD")
    return found


def _protected_observations(
    repo_root: Path,
    candidate: dict[str, Any],
    index_objects: dict[str, tuple[str, bytes] | None] | None = None,
) -> tuple[dict[str, list[dict[str, Any]]], bool]:
    try:
        return observe_current_tree(repo_root, candidate, index_objects=index_objects)
    except ObservationPathEscape as exc:
        _error("unsafe_path", "tree.protected", f"path resolves outside repository: `{exc}`")
    except CurrentTreeInspectionError as exc:
        _error("invalid_git_state", "git.index", str(exc))
    raise AssertionError("unreachable")


def run_preflight(repo_root: Path, premise_path: Path, issue_path: Path, *, decision_log: str | None = None) -> dict[str, Any]:
    candidate = _validate_candidate(repo_root, _load_json(repo_root, premise_path, "premise"))
    snapshot = candidate.pop("snapshot")
    issue = _validate_issue(repo_root, _load_json(repo_root, issue_path, "issue_readback"), candidate)
    records = _read_decisions(repo_root, decision_log or candidate["decision_log"])
    current_head = snapshot.current_head_sha
    if current_head is None or _SHA_RE.fullmatch(current_head) is None:
        _error("invalid_git_state", "tree.captured_head_sha", "repository HEAD does not resolve to a commit")
    observations: dict[str, list[dict[str, Any]]] = {"protected": [], "expected_missing": []}
    reasons: list[dict[str, str]] = []
    if issue["state"] == "CLOSED" or _marker_seen(repo_root, candidate["premise_id"], snapshot):
        reasons.append({"code": "already_shipped", "path": "issue.state", "message": "issue is closed or the exact premise marker is already reachable from current HEAD"})
    if any(record.get("status") == "accepted" and record.get("premise_id") == candidate["premise_id"] for record in records):
        reasons.append({"code": "duplicate_premise", "path": "decision_log", "message": "an accepted decision already exists for this premise ID"})
    captured = candidate["captured_issue"]
    if issue["state"] != "CLOSED" and any(issue[key] != captured[key] for key in ("body_sha256", "comments_sha256", "comment_count", "updated_at")):
        reasons.append({"code": "stale_issue", "path": "issue_readback", "message": "captured issue identity does not match the readback"})
    if current_head != candidate["captured_head_sha"]:
        reasons.append({"code": "stale_tree", "path": "tree.captured_head_sha", "message": "current HEAD moved after the premise was captured"})
    else:
        observations, drift = _protected_observations(
            repo_root, candidate, snapshot.index_objects
        )
        if drift:
            reasons.append({"code": "partial_repair", "path": "tree.protected", "message": "protected index/worktree or expected-missing paths changed before implementation"})
    reasons.sort(key=lambda item: REASON_ORDER.index(item["code"]))
    status = "accepted" if not reasons else "refused"
    record = _record(repo_root, candidate, issue, current_head, observations, reasons, status=status)
    log_path = decision_log or candidate["decision_log"]
    log_path = _relative_path(log_path, "decision_log")
    _append_decision(repo_root, log_path, record)
    return {"status": status, "exit_code": 0 if status == "accepted" else 1, "persisted": True, "decision_log": log_path, "decision": record, "non_claim": NON_CLAIM}
