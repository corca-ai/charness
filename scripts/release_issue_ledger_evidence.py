"""Evidence readers shared by the release-issue ledger contract.

This module binds receipts and captured source bytes. It deliberately does not
judge issue prose or GitHub freshness; the contract module owns disposition and
path rules, while the live tracker remains the source of truth at closeout.
"""

from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime
from pathlib import Path, PurePosixPath
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover - PyYAML is a declared dependency
    yaml = None  # type: ignore[assignment]


REPOSITORY = "corca-ai/charness"
CLASSIFICATIONS = {
    "release-blocker", "qualified-repair", "premise-refuted", "already-satisfied",
    "decision-required", "deferred", "partial-child-shipped", "cannot-ship",
}
HEX64 = re.compile(r"^[0-9a-f]{64}$")
HEX40 = re.compile(r"^[0-9a-f]{40}$")


def norm_text(value: Any) -> str:
    text = str(value or "").replace("\r\n", "\n").replace("\r", "\n")
    return "\n".join(line.rstrip() for line in text.replace("\u00a0", " ").split("\n"))


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def repo_path(repo_root: Path, raw: Any, *, field: str, errors: list[str]) -> Path | None:
    if not isinstance(raw, str) or not raw.strip():
        errors.append(f"{field}: required repo-relative path")
        return None
    candidate = PurePosixPath(raw)
    if candidate.is_absolute() or ".." in candidate.parts:
        errors.append(f"{field}: path must stay repo-relative: {raw!r}")
        return None
    return repo_root / Path(*candidate.parts)


def require_mapping(value: Any, label: str, errors: list[str]) -> dict[str, Any]:
    if not isinstance(value, dict):
        errors.append(f"{label}: expected object")
        return {}
    return value


def require_nonempty(value: Any, label: str, errors: list[str]) -> None:
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{label}: required non-empty value")


def parse_timestamp(value: Any, label: str, errors: list[str]) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{label}: ISO-8601 timestamp required")
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        errors.append(f"{label}: invalid ISO-8601 timestamp")
        return None
    if parsed.tzinfo is None:
        errors.append(f"{label}: timezone required")
        return None
    return parsed


def source_record(repo_root: Path, source_path: Path, errors: list[str], label: str) -> tuple[dict[str, Any] | None, str | None, str | None]:
    if yaml is None:
        errors.append(f"{label}: PyYAML is required to verify issue read receipts")
        return None, None, None
    if not source_path.is_file():
        errors.append(f"{label}: source read receipt does not exist")
        return None, None, None
    try:
        issue = (yaml.safe_load(source_path.read_text(encoding="utf-8")) or {})["issue"]
        comments = []
        for comment in issue.get("comments") or []:
            author = comment.get("author") or {}
            comments.append({
                "id": comment.get("id"),
                "author": author.get("login") if isinstance(author, dict) else str(author),
                "created_at": comment.get("createdAt") or "",
                "body": norm_text(comment.get("body")),
            })
        metadata = {
            "number": issue.get("number"), "url": issue.get("url") or "",
            "title": issue.get("title") or "", "state": str(issue.get("state") or "").lower(),
            "updated_at": issue.get("updatedAt") or "",
        }
        return metadata, sha256(norm_text(issue.get("body"))), sha256(canonical(comments))
    except (KeyError, TypeError, AttributeError, OSError, UnicodeError, yaml.YAMLError) as exc:
        errors.append(f"{label}: cannot parse source read receipt: {exc}")
        return None, None, None


def _receipt_metadata(meta_path: Path, row: dict[str, Any], label: str, errors: list[str]) -> None:
    if yaml is None:
        errors.append(f"{label}.meta_path: PyYAML is required to verify receipt metadata")
        return
    try:
        metadata = yaml.safe_load(meta_path.read_text(encoding="utf-8")) or {}
    except (OSError, UnicodeError, yaml.YAMLError) as exc:
        errors.append(f"{label}.meta_path: cannot parse metadata receipt: {exc}")
        return
    if not isinstance(metadata, dict):
        errors.append(f"{label}.meta_path: metadata must be an object")
        return
    for key in ("command", "head_sha", "exit_code"):
        if metadata.get(key) != row.get(key):
            errors.append(f"{label}.{key}: does not match metadata receipt")
    meta_time = parse_timestamp(str(metadata.get("captured_at")), f"{label}.meta.captured_at", errors)
    row_time = parse_timestamp(row.get("captured_at"), f"{label}.captured_at", errors)
    if meta_time is not None and row_time is not None and meta_time != row_time:
        errors.append(f"{label}.captured_at: does not match metadata receipt")


def validate_receipt(repo_root: Path, receipt: Any, label: str, head_sha: str, errors: list[str]) -> None:  # noqa: C901
    row = require_mapping(receipt, label, errors)
    for key in ("command", "raw_output_path", "meta_path", "head_sha", "captured_at", "raw_sha256", "meta_sha256"):
        require_nonempty(row.get(key), f"{label}.{key}", errors)
    if row.get("head_sha") != head_sha:
        errors.append(f"{label}.head_sha: differs from ledger head_sha")
    if not isinstance(row.get("exit_code"), int):
        errors.append(f"{label}.exit_code: required integer")
    paths: dict[str, Path | None] = {}
    for key in ("raw_output_path", "meta_path"):
        path = repo_path(repo_root, row.get(key), field=f"{label}.{key}", errors=errors)
        paths[key] = path
        if path is not None and not path.is_file():
            errors.append(f"{label}.{key}: file does not exist")
        digest_key = "raw_sha256" if key == "raw_output_path" else "meta_sha256"
        if path is not None and path.is_file():
            if not isinstance(row.get(digest_key), str) or not HEX64.fullmatch(row[digest_key]):
                errors.append(f"{label}.{digest_key}: lowercase SHA-256 required")
            elif hashlib.sha256(path.read_bytes()).hexdigest() != row[digest_key]:
                errors.append(f"{label}.{digest_key}: does not match receipt file")
    if paths["meta_path"] is not None and paths["meta_path"].is_file():
        _receipt_metadata(paths["meta_path"], row, label, errors)


def validate_snapshot(repo_root: Path, snapshot: dict[str, Any], errors: list[str]) -> list[int]:
    numbers = snapshot.get("numbers")
    if not isinstance(numbers, list) or not all(isinstance(n, int) and not isinstance(n, bool) for n in numbers):
        errors.append("ledger.activation_issue_snapshot.numbers: integer list required")
        numbers = []
    if snapshot.get("list_truncated") is not False:
        errors.append("ledger.activation_issue_snapshot.list_truncated: must be false")
    if snapshot.get("count") != len(numbers):
        errors.append("ledger.activation_issue_snapshot.count: does not equal numbers length")
    raw_path = repo_path(repo_root, snapshot.get("path"), field="ledger.activation_issue_snapshot.path", errors=errors)
    if raw_path is None or not raw_path.is_file():
        if raw_path is not None:
            errors.append("ledger.activation_issue_snapshot.path: file does not exist")
        return numbers
    try:
        raw_bytes = raw_path.read_bytes()
        if snapshot.get("raw_sha256") != hashlib.sha256(raw_bytes).hexdigest():
            errors.append("ledger.activation_issue_snapshot.raw_sha256: does not match raw snapshot")
        raw = json.loads(raw_bytes.decode("utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        errors.append(f"ledger.activation_issue_snapshot: cannot read raw snapshot: {exc}")
        return numbers
    if not isinstance(raw, list):
        errors.append("ledger.activation_issue_snapshot.path: raw snapshot must be an issue list")
        return numbers
    derived = [item.get("number") for item in raw if isinstance(item, dict) and isinstance(item.get("number"), int) and not isinstance(item.get("number"), bool)]
    if len(derived) != len(raw):
        errors.append("ledger.activation_issue_snapshot.raw: every issue needs a non-boolean number")
    if derived != numbers:
        errors.append("ledger.activation_issue_snapshot.numbers: does not match raw snapshot order")
    if snapshot.get("count") != len(derived):
        errors.append("ledger.activation_issue_snapshot.count: does not match raw snapshot")
    if snapshot.get("numbers_sha256") != sha256(canonical(numbers)):
        errors.append("ledger.activation_issue_snapshot.numbers_sha256: does not match numbers")
    if len(set(derived)) != len(derived):
        errors.append("ledger.activation_issue_snapshot.raw: duplicate issue number")
    return derived


def validate_post_lock_exceptions(repo_root: Path, exceptions: Any, activation_numbers: set[int], head_sha: str, captured_at: datetime | None, errors: list[str]) -> None:  # noqa: C901
    if not isinstance(exceptions, list):
        errors.append("ledger.post_lock_exceptions: required list")
        return
    seen: set[str] = set()
    for index, exception in enumerate(exceptions):
        label = f"post_lock_exceptions[{index}]"
        row = require_mapping(exception, label, errors)
        exception_id = row.get("exception_id")
        if not isinstance(exception_id, str) or not exception_id.strip() or exception_id in seen:
            errors.append(f"{label}.exception_id: unique non-empty id required")
        seen.add(str(exception_id))
        if not isinstance(row.get("issue_number"), int) or isinstance(row.get("issue_number"), bool):
            errors.append(f"{label}.issue_number: integer required")
        for key in ("issue_url", "observed_at", "observed_head_sha", "lock_head_sha", "release_impact", "source_read_path"):
            require_nonempty(row.get(key), f"{label}.{key}", errors)
        if row.get("issue_number") in activation_numbers:
            errors.append(f"{label}.issue_number: post-lock exception must be outside activation snapshot")
        observed_at = parse_timestamp(row.get("observed_at"), f"{label}.observed_at", errors)
        if captured_at is not None and observed_at is not None and observed_at <= captured_at:
            errors.append(f"{label}.observed_at: must be after ledger capture")
        expected_url = f"https://github.com/{REPOSITORY}/issues/{row.get('issue_number')}"
        if row.get("issue_url") != expected_url:
            errors.append(f"{label}.issue_url: must match issue number in the Charness repository")
        if row.get("lock_head_sha") != head_sha:
            errors.append(f"{label}.lock_head_sha: must equal ledger head_sha")
        if not isinstance(row.get("observed_head_sha"), str) or not (HEX40.fullmatch(row["observed_head_sha"]) or HEX64.fullmatch(row["observed_head_sha"])):
            errors.append(f"{label}.observed_head_sha: commit SHA required")
        if row.get("classification") != "release-blocker":
            errors.append(f"{label}.classification: must be release-blocker")
        premise = require_mapping(row.get("premise"), f"{label}.premise", errors)
        require_nonempty(premise.get("exact_command"), f"{label}.premise.exact_command", errors)
        if premise.get("verdict") != "post-lock-release-blocker-reproduced":
            errors.append(f"{label}.premise.verdict: reproduced post-lock blocker required")
        if not isinstance(premise.get("exit"), int) or premise.get("exit") == 0:
            errors.append(f"{label}.premise.exit: nonzero reproduced failure required")
        evidence = repo_path(repo_root, premise.get("evidence_path"), field=f"{label}.premise.evidence_path", errors=errors)
        if evidence is not None and not evidence.is_file():
            errors.append(f"{label}.premise.evidence_path: file does not exist")
        source_path = repo_path(repo_root, row.get("source_read_path"), field=f"{label}.source_read_path", errors=errors)
        if source_path is not None:
            source, _, _ = source_record(repo_root, source_path, errors, f"{label}.source_read_path")
            if source is not None:
                if source.get("number") != row.get("issue_number"):
                    errors.append(f"{label}.source_read_path: issue number does not match exception")
                if source.get("url") != row.get("issue_url"):
                    errors.append(f"{label}.source_read_path: issue URL does not match exception")
