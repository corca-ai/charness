"""Pure contracts for issue-native ``/goal #N`` pickup."""

from __future__ import annotations

import hashlib
import json
import re
from typing import Any

OBJECTIVE_RE = re.compile(r"^/goal +#([1-9][0-9]*)$")
KEY_RE = re.compile(r"<!--\s*charness-work-item-key:\s*([^\s]+)\s*-->")
SHA_RE = re.compile(r"^[0-9a-f]{64}$")
GOAL_RUN_SCHEMA = "charness.goal-binding/v1"
VERIFIED_BOOTSTRAP = "verified-target-roundtrip"


class PickupError(ValueError):
    """Typed refusal that tells the operator which identity failed."""

    def __init__(self, code: str, message: str, *, details: Any = None) -> None:
        self.code = code
        self.details = details
        super().__init__(message)


def parse_objective(value: Any) -> int:
    if not isinstance(value, str):
        raise PickupError("objective-invalid", "objective must be text matching `/goal #N`")
    match = OBJECTIVE_RE.fullmatch(value.strip())
    if match is None:
        raise PickupError("objective-invalid", "objective must match `/goal #N` exactly")
    return int(match.group(1))


def _sha(value: Any, field: str) -> str:
    if not isinstance(value, str) or SHA_RE.fullmatch(value) is None:
        raise PickupError("metadata-invalid", f"{field} must be a lowercase SHA-256")
    return value


def validate_metadata(
    metadata: Any, *, repo: str, parent_number: int, parent_url: str
) -> dict[str, Any]:
    if not isinstance(metadata, dict):
        raise PickupError("metadata-invalid", "Goal Run metadata must be an object")
    required = {
        "binding_schema",
        "binding_path",
        "binding_sha256",
        "draft_path",
        "draft_sha256",
        "initial_graph_sha256",
        "bootstrap_verification",
        "parent_identity",
        "current_membership_sha256",
    }
    missing = sorted(required - set(metadata))
    if missing:
        raise PickupError("metadata-incomplete", f"Goal Run metadata is missing {missing!r}")
    if metadata["binding_schema"] != GOAL_RUN_SCHEMA:
        raise PickupError("metadata-invalid", "Goal Run metadata names an unsupported binding schema")
    identity = metadata["parent_identity"]
    if identity != {"repo": repo, "number": parent_number, "url": parent_url}:
        raise PickupError("parent-mismatch", "Goal Run metadata parent identity differs from the provider read")
    if metadata["bootstrap_verification"] != VERIFIED_BOOTSTRAP:
        raise PickupError(
            "establishment-pending",
            "Goal Run establishment is not verified for `/goal` pickup",
            details={"bootstrap_verification": metadata["bootstrap_verification"]},
        )
    for field in (
        "binding_sha256",
        "draft_sha256",
        "initial_graph_sha256",
        "current_membership_sha256",
    ):
        _sha(metadata[field], f"metadata.{field}")
    for field in ("binding_path", "draft_path"):
        if not isinstance(metadata[field], str) or not metadata[field].strip():
            raise PickupError("metadata-invalid", f"metadata.{field} must be a non-empty repo-relative path")
    return dict(metadata)


def membership_digest(repo: str, parent_number: int, children: list[dict[str, Any]]) -> str:
    rows: list[dict[str, Any]] = []
    expected_parent_url = f"https://api.github.com/repos/{repo}/issues/{parent_number}"
    for index, child in enumerate(children):
        number = child.get("number")
        url = child.get("url")
        parent_url = child.get("parent_issue_url")
        if type(number) is not int or number <= 0:
            raise PickupError("graph-invalid", f"child {index} has no positive issue number")
        if url != f"https://github.com/{repo}/issues/{number}":
            raise PickupError("graph-identity-mismatch", f"child {repo}#{number} has a foreign issue URL")
        if parent_url != expected_parent_url:
            raise PickupError("graph-parent-mismatch", f"child {repo}#{number} is not linked to the requested parent")
        rows.append({"number": number, "parent_issue_url": parent_url, "repo": repo, "url": url})
    if len({row["number"] for row in rows}) != len(rows):
        raise PickupError("graph-invalid", "provider returned duplicate child issue numbers")
    raw = json.dumps(sorted(rows, key=lambda row: row["number"]), sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def work_item_key(body: Any) -> str | None:
    if not isinstance(body, str):
        return None
    matches = KEY_RE.findall(body)
    if len(matches) != 1:
        return None
    return matches[0]


def _headings(body: str) -> set[str]:
    return {
        line[3:].strip().lower()
        for line in body.splitlines()
        if line.startswith("## ")
    }


def executable_body_report(body: Any, expected_key: str) -> dict[str, Any]:
    if not isinstance(body, str):
        return {"ok": False, "reason": "body is not text"}
    key = work_item_key(body)
    if key != expected_key:
        return {"ok": False, "reason": "managed Work Item key marker is missing or mismatched"}
    headings = _headings(body)
    checks = {
        "purpose": any(value.startswith("purpose") for value in headings),
        "contract": any(value.startswith(("bounded contract", "owned change", "owned surfaces")) for value in headings),
        "acceptance": any("acceptance" in value or value.startswith("verification") for value in headings),
        "evidence": any("evidence boundary" in value or "non-claims" in value for value in headings),
    }
    missing = sorted(name for name, present in checks.items() if not present)
    return {"ok": not missing, "key": key, "missing": missing, "headings": sorted(headings)}


def reconcile_and_select(  # noqa: C901 -- selection and membership reconciliation are one atomic contract
    children: list[dict[str, Any]], binding_items: list[dict[str, Any]], *, repo: str
) -> dict[str, Any]:
    items = {item["key"]: item for item in binding_items}
    if len(items) != len(binding_items):
        raise PickupError("binding-invalid", "binding contains duplicate Work Item keys")
    by_key: dict[str, dict[str, Any]] = {}
    by_number: dict[int, dict[str, Any]] = {}
    for item in binding_items:
        issue = item.get("issue")
        if isinstance(issue, dict) and type(issue.get("number")) is int:
            by_number[issue["number"]] = item
    invalid_open: list[dict[str, Any]] = []
    for child in children:
        number = child["number"]
        item = by_number.get(number)
        key = work_item_key(child.get("body"))
        if item is None and child.get("state") == "OPEN":
            item = items.get(key)
        if item is None:
            if child.get("state") == "CLOSED":
                continue
            invalid_open.append({"number": number, "reason": "open child is not an approved Work Item"})
            continue
        if item.get("issue"):
            expected = item["issue"]
            if expected.get("repo") != repo or expected.get("number") != number:
                raise PickupError("child-identity-mismatch", f"binding identity for {item['key']} differs from live child #{number}")
        if child.get("state") == "OPEN":
            body_report = executable_body_report(child.get("body"), item["key"])
            if not body_report["ok"]:
                invalid_open.append({"number": number, "key": item["key"], "reason": body_report})
        by_key[item["key"]] = {**child, "work_item": item}
    missing = sorted(set(items) - set(by_key))
    if missing:
        raise PickupError("graph-work-item-mismatch", "live graph does not expose every approved Work Item", details={"missing_keys": missing})
    candidates: list[dict[str, Any]] = []
    blocked: list[dict[str, Any]] = []
    for key, row in by_key.items():
        if row.get("state") != "OPEN":
            continue
        if any(entry.get("number") == row.get("number") for entry in invalid_open):
            continue
        item = row["work_item"]
        dependencies = item.get("dependencies", [])
        unmet = [dep for dep in dependencies if dep not in by_key or by_key[dep].get("state") != "CLOSED"]
        if unmet:
            blocked.append({"key": key, "number": row["number"], "unmet_dependencies": unmet})
            continue
        candidates.append({"key": key, "number": row["number"], "repo": repo, "rank": item["rank"], "dependencies": dependencies, "title": row.get("title")})
    if not candidates:
        if invalid_open:
            raise PickupError("no-executable-child", "open children are incomplete or stale", details={"invalid_open": invalid_open, "blocked": blocked})
        raise PickupError("dependency-blocked", "every open child has an unmet dependency", details={"blocked": blocked})
    selected = sorted(candidates, key=lambda row: (row["rank"], row["key"], row["repo"], row["number"]))[0]
    return {"selected_child": selected, "work_items": by_key, "blocked": blocked, "invalid_open": invalid_open}
