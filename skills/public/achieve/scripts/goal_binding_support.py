"""Shared schema, identity, path, and manifest checks for Goal Binding V1."""

from __future__ import annotations

import hashlib
import json
import os
import re
from pathlib import Path, PurePosixPath
from typing import Any, Mapping
from urllib.parse import urlparse

SCHEMA = "charness.goal-binding/v1"
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
KEY_RE = re.compile(r"^[a-z0-9][a-z0-9._-]*$")
REPO_RE = re.compile(
    r"^[A-Za-z0-9](?:[A-Za-z0-9_.-]*[A-Za-z0-9])?/[A-Za-z0-9](?:[A-Za-z0-9_.-]*[A-Za-z0-9])?$"
)

TOP_LEVEL_FIELDS = frozenset(
    {"kind", "draft", "approval", "parent", "approved_work_items", "approved_work_items_sha256"}
)
DRAFT_FIELDS = frozenset({"path", "sha256"})
APPROVAL_FIELDS = frozenset({"briefing_sha256", "response", "session_id", "observed_at"})
PARENT_FIELDS = frozenset({"repo", "number", "url"})
WORK_ITEM_FIELDS = frozenset({"key", "intent", "issue", "dependencies", "rank", "observed"})
OPTIONAL_WORK_ITEM_FIELDS = frozenset({"body_policy", "body_sha256"})
# Compatibility alias for callers that imported the old complete field set.
ITEM_FIELDS = WORK_ITEM_FIELDS | OPTIONAL_WORK_ITEM_FIELDS
ISSUE_FIELDS = frozenset({"repo", "number", "url"})
OBSERVED_FIELDS = frozenset({"state", "title_sha256"})
OPTIONAL_OBSERVED_FIELDS = frozenset({"body_sha256"})
BODY_POLICIES = frozenset({"managed", "managed-addendum", "preserve-closed-evidence"})
FORBIDDEN_STATE_FIELDS = frozenset(
    {
        "status",
        "progress",
        "current_child",
        "establishment",
        "terminal",
        "observations",
        "observation",
        "observation_path",
        "provider_state",
        "parent_body",
        "readback",
        "attempt_id",
        "receipt",
    }
)


class BindingError(ValueError):
    """A typed refusal to consume or create an invalid Goal Binding."""

    def __init__(self, code: str, message: str) -> None:
        self.code = code
        super().__init__(f"{code}: {message}")


def canonical_json_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
    ).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    try:
        return sha256_bytes(path.read_bytes())
    except (OSError, ValueError) as exc:
        raise BindingError("draft-missing", f"could not read file {path}: {exc}") from exc


def _require_object(value: Any, code: str, context: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise BindingError(code, f"{context} must be a JSON object")
    return value


def _require_fields(
    value: Mapping[str, Any],
    expected: frozenset[str],
    context: str,
    *,
    optional: frozenset[str] = frozenset(),
) -> None:
    fields = set(value)
    missing = sorted(expected - fields)
    extra = sorted(fields - expected - optional)
    if missing:
        raise BindingError("schema-invalid", f"{context} is missing fields {missing!r}")
    if extra:
        forbidden = sorted(set(extra) & FORBIDDEN_STATE_FIELDS)
        if forbidden:
            raise BindingError(
                "state-field-forbidden", f"{context} contains state fields {forbidden!r}"
            )
        raise BindingError("schema-invalid", f"{context} has unknown fields {extra!r}")


def _require_text(value: Any, code: str, context: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise BindingError(code, f"{context} must be a non-empty string")
    return value


def _require_sha(value: Any, code: str, context: str) -> str:
    if not isinstance(value, str) or not SHA256_RE.fullmatch(value):
        raise BindingError(code, f"{context} must be 64 lowercase hexadecimal characters")
    return value


def _repo_url(repo: str, number: int) -> str:
    return f"https://github.com/{repo}/issues/{number}"


def _validate_identity(
    value: Any, *, context: str, expected_repo: str | None = None
) -> dict[str, Any]:
    identity = _require_object(value, "schema-invalid", context)
    _require_fields(identity, ISSUE_FIELDS, context)
    repo = identity["repo"]
    number = identity["number"]
    url = identity["url"]
    if not isinstance(repo, str) or not REPO_RE.fullmatch(repo):
        raise BindingError(
            "schema-invalid", f"{context}.repo is not a canonical owner/repository slug"
        )
    if expected_repo is not None and repo != expected_repo:
        raise BindingError("parent-mismatch", f"{context}.repo is not {expected_repo!r}")
    if type(number) is not int or number <= 0:
        raise BindingError("schema-invalid", f"{context}.number must be positive")
    expected_url = _repo_url(repo, number)
    try:
        parsed = urlparse(url) if isinstance(url, str) else None
    except ValueError as exc:
        raise BindingError("parent-mismatch", f"{context}.url is not parseable") from exc
    if (
        not isinstance(url, str)
        or url != expected_url
        or parsed is None
        or parsed.scheme != "https"
        or parsed.netloc != "github.com"
        or parsed.path != f"/{repo}/issues/{number}"
        or parsed.params
        or parsed.query
        or parsed.fragment
    ):
        raise BindingError("parent-mismatch", f"{context}.url is not canonical")
    return identity


def _validate_relative_text_path(value: Any, *, context: str, suffix: str) -> str:
    if not isinstance(value, str) or not value:
        raise BindingError(
            "path-invalid", f"{context} must be a non-empty repository-relative path"
        )
    if "\x00" in value:
        raise BindingError("path-invalid", f"{context} contains an invalid NUL character")
    if "\\" in value:
        raise BindingError("path-invalid", f"{context} must use repository-relative separators")
    pure = PurePosixPath(value)
    if pure.is_absolute() or any(part in {"", ".", ".."} for part in pure.parts):
        raise BindingError("path-invalid", f"{context} must not escape the repository")
    if pure.as_posix() != value:
        raise BindingError("path-invalid", f"{context} must use its canonical relative spelling")
    if pure.suffix != suffix:
        raise BindingError("path-invalid", f"{context} must end in {suffix}")
    return value


def _reject_symlink_components(root: Path, candidate: Path, *, context: str) -> None:
    try:
        relative = candidate.relative_to(root)
    except ValueError as exc:
        raise BindingError("path-invalid", f"{context} resolves outside the repository") from exc
    current = root
    for part in relative.parts:
        current /= part
        try:
            linked = os.path.lexists(current) and current.is_symlink()
        except (OSError, ValueError) as exc:
            raise BindingError("path-invalid", f"could not inspect {context}: {exc}") from exc
        if linked:
            raise BindingError("path-invalid", f"{context} must not traverse a symlink")


def _repo_path(
    root: Path,
    value: str | Path,
    *,
    context: str,
    suffix: str,
    require_file: bool,
    missing_code: str,
) -> tuple[str, Path, Path]:
    if not isinstance(value, (str, Path)):
        raise BindingError("path-invalid", f"{context} must be a repository-relative path")
    raw = os.fspath(value)
    if "\x00" in raw:
        raise BindingError("path-invalid", f"{context} contains an invalid NUL character")
    if "\\" in raw:
        raise BindingError("path-invalid", f"{context} must use repository-relative separators")
    raw_path = Path(raw)
    if raw_path.is_absolute():
        try:
            relative = raw_path.relative_to(root)
        except ValueError as exc:
            raise BindingError(
                "path-invalid", f"{context} must stay inside the repository"
            ) from exc
        relative_text = relative.as_posix()
    else:
        relative_text = raw
    _validate_relative_text_path(relative_text, context=context, suffix=suffix)
    candidate = root.joinpath(*PurePosixPath(relative_text).parts)
    _reject_symlink_components(root, candidate, context=context)
    try:
        resolved = candidate.resolve(strict=False)
    except (OSError, ValueError) as exc:
        raise BindingError("path-invalid", f"could not resolve {context}: {exc}") from exc
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise BindingError("path-invalid", f"{context} resolves outside the repository") from exc
    if require_file:
        try:
            present = candidate.is_file()
        except (OSError, ValueError) as exc:
            raise BindingError(missing_code, f"could not inspect {context}: {exc}") from exc
        if not present:
            raise BindingError(missing_code, f"{context} does not name an existing file")
    return relative_text, candidate, resolved


def _relative_repo_path(root: Path, value: Any, *, context: str, suffix: str) -> tuple[str, Path]:
    # Payload paths are strings in the schema and must remain relative.  The
    # public API path arguments separately allow absolute paths inside root.
    _validate_relative_text_path(value, context=context, suffix=suffix)
    relative, _, resolved = _repo_path(
        root,
        value,
        context=context,
        suffix=suffix,
        require_file=True,
        missing_code="draft-missing",
    )
    return relative, resolved


def _validate_item(item: Any, *, parent: dict[str, Any]) -> dict[str, Any]:  # noqa: C901 -- item validation owns the complete cross-field contract
    value = _require_object(item, "schema-invalid", "approved work item")
    _require_fields(
        value,
        WORK_ITEM_FIELDS,
        "approved work item",
        optional=OPTIONAL_WORK_ITEM_FIELDS,
    )
    key = value["key"]
    if not isinstance(key, str) or not KEY_RE.fullmatch(key):
        raise BindingError("schema-invalid", "work item key has invalid form")

    intent = value["intent"]
    if not isinstance(intent, str) or intent not in {"create", "reuse"}:
        raise BindingError("schema-invalid", f"work item {key!r} has invalid intent")
    dependencies = value["dependencies"]
    if not isinstance(dependencies, list) or any(
        not isinstance(dep, str) or not KEY_RE.fullmatch(dep) for dep in dependencies
    ):
        raise BindingError("schema-invalid", f"work item {key!r} dependencies are invalid")
    if dependencies != sorted(set(dependencies)) or key in dependencies:
        raise BindingError("schema-invalid", f"work item {key!r} dependencies are not canonical")
    rank = value["rank"]
    if type(rank) is not int or rank <= 0:
        raise BindingError("schema-invalid", f"work item {key!r} rank must be positive")

    policy = value.get("body_policy")
    if policy is not None and (not isinstance(policy, str) or policy not in BODY_POLICIES):
        raise BindingError("body-policy-invalid", f"work item {key!r} body policy is invalid")
    body_sha = value.get("body_sha256")
    if body_sha is not None and not isinstance(body_sha, str):
        raise BindingError(
            "schema-invalid", f"work item {key!r}.body_sha256 must be a hash or null"
        )
    if body_sha is not None:
        _require_sha(body_sha, "schema-invalid", f"work item {key!r}.body_sha256")

    issue = value["issue"]
    observed = value["observed"]
    if intent == "create":
        if policy == "preserve-closed-evidence":
            raise BindingError(
                "body-policy-invalid",
                f"new item {key!r} cannot preserve closed evidence",
            )
        if issue is not None or observed is not None:
            raise BindingError(
                "schema-invalid", f"new item {key!r} cannot carry observed issue state"
            )
        return value

    if issue is None or observed is None:
        raise BindingError("schema-invalid", f"reused item {key!r} needs issue and observation")
    issue_value = _validate_identity(
        issue, context=f"work item {key!r}.issue", expected_repo=parent["repo"]
    )
    if issue_value["number"] == parent["number"]:
        raise BindingError("parent-mismatch", f"work item {key!r} cannot reuse the Goal Run parent")
    observed_value = _require_object(observed, "schema-invalid", f"work item {key!r}.observed")
    _require_fields(
        observed_value,
        OBSERVED_FIELDS,
        f"work item {key!r}.observed",
        optional=OPTIONAL_OBSERVED_FIELDS,
    )
    state = observed_value["state"]
    if not isinstance(state, str) or state not in {"OPEN", "CLOSED"}:
        raise BindingError("schema-invalid", f"work item {key!r} has invalid observed state")
    _require_sha(
        observed_value["title_sha256"], "schema-invalid", f"work item {key!r}.title_sha256"
    )
    observed_body_sha = observed_value.get("body_sha256")
    if observed_body_sha is not None:
        _require_sha(observed_body_sha, "schema-invalid", f"work item {key!r}.observed.body_sha256")
    if policy == "preserve-closed-evidence" and state != "CLOSED":
        raise BindingError(
            "body-policy-invalid",
            f"work item {key!r} may preserve evidence only for a closed reused issue",
        )
    if state == "CLOSED" and policy != "preserve-closed-evidence":
        raise BindingError(
            "body-policy-invalid",
            f"closed reused item {key!r} requires preserve-closed-evidence",
        )
    return value


def _validate_manifest(items: Any, *, parent: dict[str, Any]) -> list[dict[str, Any]]:
    if not isinstance(items, list) or not items:
        raise BindingError("schema-invalid", "approved_work_items must be a non-empty list")
    validated = [_validate_item(item, parent=parent) for item in items]
    keys = [item["key"] for item in validated]
    if keys != sorted(keys) or len(keys) != len(set(keys)):
        raise BindingError("schema-invalid", "approved work items must be key-sorted and unique")
    key_set = set(keys)
    for item in validated:
        unknown_deps = sorted(set(item["dependencies"]) - key_set)
        if unknown_deps:
            raise BindingError(
                "schema-invalid", f"work item {item['key']!r} has unknown dependencies"
            )

    by_key = {item["key"]: item for item in validated}
    visit_state: dict[str, int] = {}

    def visit(key: str, trail: tuple[str, ...] = ()) -> None:
        state = visit_state.get(key, 0)
        if state == 1:
            cycle = " -> ".join((*trail, key))
            raise BindingError("dependency-cycle", f"approved work-item dependency cycle: {cycle}")
        if state == 2:
            return
        visit_state[key] = 1
        for dependency in by_key[key]["dependencies"]:
            visit(dependency, (*trail, key))
        visit_state[key] = 2

    for key in keys:
        visit(key)

    ranks = {item["key"]: item["rank"] for item in validated}
    for item in validated:
        if any(ranks[dependency] >= item["rank"] for dependency in item["dependencies"]):
            raise BindingError(
                "dependency-rank-invalid",
                f"work item {item['key']!r} must rank strictly after every dependency",
            )

    seen_issue: dict[tuple[str, int], str] = {}
    for item in validated:
        issue = item["issue"]
        if issue is None:
            continue
        identity = (issue["repo"], issue["number"])
        prior = seen_issue.get(identity)
        if prior is not None:
            raise BindingError(
                "graph-identity-collision",
                f"work items {prior!r} and {item['key']!r} reuse the same issue",
            )
        seen_issue[identity] = item["key"]
    return validated
