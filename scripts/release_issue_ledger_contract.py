"""Disposition and path contract for the activation-time release ledger."""

from __future__ import annotations

from collections import Counter
from datetime import datetime
from pathlib import Path, PurePosixPath
from typing import Any


def _load_repo_runtime_bootstrap():
    pathlib, sys = __import__("pathlib"), __import__("sys")
    marker = ("scripts", "adapter_lib.py")
    parents = pathlib.Path(__file__).resolve().parents
    root = next((p for p in parents if p.joinpath(*marker).is_file()), None)
    if root is not None and str(root) not in sys.path:
        sys.path.insert(0, str(root))


_load_repo_runtime_bootstrap()

try:
    from scripts.release_issue_ledger_evidence import (
        CLASSIFICATIONS,
        HEX40,
        HEX64,
        REPOSITORY,
        parse_timestamp,
        repo_path,
        require_mapping,
        require_nonempty,
        source_record,
        validate_post_lock_exceptions,
        validate_receipt,
        validate_snapshot,
    )
except ImportError:  # pragma: no cover - direct execution from scripts/
    from release_issue_ledger_evidence import (  # type: ignore[no-redef]
        CLASSIFICATIONS,
        HEX40,
        HEX64,
        REPOSITORY,
        parse_timestamp,
        repo_path,
        require_mapping,
        require_nonempty,
        source_record,
        validate_post_lock_exceptions,
        validate_receipt,
        validate_snapshot,
    )


SCHEMA_VERSION = "charness.release-issue-ledger.v1"
CLOSE_DISPOSITIONS = {"leave-open", "close-after-publish", "close-now"}
ADMISSION_VERDICTS = {"current-reproducer", "current-contract-gap"}
DEFER_REASONS = {"missing-current-reproducer", "current-supported-path-passes", "missing-bounded-child", "external-fixture-missing"}
IMPACT_PREFIXES = ("release-blocker:", "release-train-quality:")


def require_string_list(value: Any, label: str, errors: list[str], *, nonempty: bool = False) -> None:
    if not isinstance(value, list):
        errors.append(f"{label}: list required")
        return
    for index, item in enumerate(value):
        if not isinstance(item, str) or not item.strip():
            errors.append(f"{label}[{index}]: non-empty string required")
    if nonempty and not value:
        errors.append(f"{label}: non-empty list required")


def path_overlaps(left: str, right: str) -> bool:
    a, b = PurePosixPath(left), PurePosixPath(right)
    return a == b or a in b.parents or b in a.parents


def path_within_budget(path: str, budget: str) -> bool:
    return path == budget or path.startswith(budget.rstrip("/") + "/")


def validate_amendments(issue: dict[str, Any], label: str, repo_root: Path, head_sha: str, captured_at: datetime | None, errors: list[str]) -> None:  # noqa: C901
    amendments = issue.get("amendments")
    if not isinstance(amendments, list):
        errors.append(f"{label}.amendments: append-only list required")
        return
    locked = issue.get("locked_classification")
    if locked not in CLASSIFICATIONS:
        errors.append(f"{label}.locked_classification: required locked enum")
    if issue.get("locked_head_sha") != head_sha:
        errors.append(f"{label}.locked_head_sha: must equal ledger head_sha")
    seen: set[str] = set()
    previous_to: str | None = None
    previous_time: datetime | None = None
    for index, amendment in enumerate(amendments):
        prefix = f"{label}.amendments[{index}]"
        row = require_mapping(amendment, prefix, errors)
        amendment_id = row.get("amendment_id")
        if not isinstance(amendment_id, str) or not amendment_id.strip() or amendment_id in seen:
            errors.append(f"{prefix}.amendment_id: unique non-empty id required")
        seen.add(str(amendment_id))
        for key in ("recorded_at", "from_classification", "to_classification", "reason", "owner", "evidence_path"):
            require_nonempty(row.get(key), f"{prefix}.{key}", errors)
        recorded = parse_timestamp(row.get("recorded_at"), f"{prefix}.recorded_at", errors)
        if captured_at is not None and recorded is not None and recorded <= captured_at:
            errors.append(f"{prefix}.recorded_at: must be after ledger capture")
        if previous_time is not None and recorded is not None and recorded <= previous_time:
            errors.append(f"{prefix}.recorded_at: amendment timestamps must increase")
        if row.get("from_classification") not in CLASSIFICATIONS or row.get("to_classification") not in CLASSIFICATIONS:
            errors.append(f"{prefix}: invalid classification transition")
        if previous_to is None and row.get("from_classification") != locked:
            errors.append(f"{prefix}: first amendment does not start at locked classification")
        if previous_to is not None and row.get("from_classification") != previous_to:
            errors.append(f"{prefix}: amendment chain overwrites prior history")
        previous_to, previous_time = row.get("to_classification"), recorded
        evidence = repo_path(repo_root, row.get("evidence_path"), field=f"{prefix}.evidence_path", errors=errors)
        if evidence is not None and not evidence.is_file():
            errors.append(f"{prefix}.evidence_path: file does not exist")
    if not amendments and locked != issue.get("classification"):
        errors.append(f"{label}: current classification differs from locked classification without amendment")
    if amendments and previous_to != issue.get("classification"):
        errors.append(f"{label}.amendments: final transition does not reach current classification")


def validate_issue(repo_root: Path, issue: Any, index: int, head_sha: str, captured_at: datetime | None, errors: list[str]) -> None:  # noqa: C901
    label = f"issues[{index}]"
    row = require_mapping(issue, label, errors)
    number = row.get("number")
    if not isinstance(number, int) or isinstance(number, bool) or number <= 0:
        errors.append(f"{label}.number: positive integer required")
    for key in ("url", "title", "state", "updated_at", "lane_id", "acceptance_owner"):
        require_nonempty(row.get(key), f"{label}.{key}", errors)
    for key in ("body_sha256", "comments_sha256"):
        if not isinstance(row.get(key), str) or not HEX64.fullmatch(row[key]):
            errors.append(f"{label}.{key}: lowercase SHA-256 required")
    classification = row.get("classification")
    if classification not in CLASSIFICATIONS:
        errors.append(f"{label}.classification: invalid classification {classification!r}")
    if row.get("close_disposition") not in CLOSE_DISPOSITIONS:
        errors.append(f"{label}.close_disposition: invalid disposition")
    premise = require_mapping(row.get("premise"), f"{label}.premise", errors)
    for key in ("exact_command", "evidence_path", "verdict"):
        require_nonempty(premise.get(key), f"{label}.premise.{key}", errors)
    if not isinstance(premise.get("exit"), int) or isinstance(premise.get("exit"), bool):
        errors.append(f"{label}.premise.exit: required integer")
    evidence = repo_path(repo_root, premise.get("evidence_path"), field=f"{label}.premise.evidence_path", errors=errors)
    if evidence is not None and not evidence.is_file():
        errors.append(f"{label}.premise.evidence_path: file does not exist")
    source_path = repo_path(repo_root, row.get("source_read_path"), field=f"{label}.source_read_path", errors=errors)
    if source_path is not None:
        source, body_hash, comments_hash = source_record(repo_root, source_path, errors, f"{label}.source_read_path")
        if source is not None:
            for key in ("number", "url", "title", "state", "updated_at"):
                if source.get(key) != row.get(key):
                    errors.append(f"{label}.{key}: does not match source read receipt")
        if body_hash is not None and body_hash != row.get("body_sha256"):
            errors.append(f"{label}.body_sha256: does not match normalized source read")
        if comments_hash is not None and comments_hash != row.get("comments_sha256"):
            errors.append(f"{label}.comments_sha256: does not match normalized source read")
    for key in ("acceptance_assertions", "allowed_paths", "dependencies", "proof_commands"):
        require_string_list(row.get(key), f"{label}.{key}", errors)
    for path_index, raw_path in enumerate(row.get("allowed_paths") or []):
        repo_path(repo_root, raw_path, field=f"{label}.allowed_paths[{path_index}]", errors=errors)
    release_evidence = row.get("release_content_evidence_path")
    if classification in {"qualified-repair", "release-blocker"}:
        if premise.get("verdict") not in ADMISSION_VERDICTS:
            errors.append(f"{label}: admitted row requires current reproducer or current contract-gap verdict")
        if not isinstance(row.get("release_impact"), str) or not any(row["release_impact"].startswith(prefix) for prefix in IMPACT_PREFIXES):
            errors.append(f"{label}: admitted row requires meaningful release impact")
        for key in ("acceptance_assertions", "proof_commands", "allowed_paths"):
            if not isinstance(row.get(key), list) or not row[key]:
                errors.append(f"{label}: admitted row requires non-empty {key}")
        carrier = repo_path(repo_root, release_evidence, field=f"{label}.release_content_evidence_path", errors=errors)
        if carrier is not None and not carrier.is_file():
            errors.append(f"{label}.release_content_evidence_path: file does not exist")
        if row.get("post_publication_closeout_path") is not None:
            errors.append(f"{label}.post_publication_closeout_path: must be null before publication")
    elif release_evidence is not None:
        repo_path(repo_root, release_evidence, field=f"{label}.release_content_evidence_path", errors=errors)
    if classification == "deferred" and row.get("defer_reason") not in DEFER_REASONS:
        errors.append(f"{label}: deferred row requires a named defer_reason")
    if classification == "decision-required":
        require_nonempty(row.get("decision_owner"), f"{label}.decision_owner", errors)
        require_nonempty(row.get("decision_question"), f"{label}.decision_question", errors)
    if classification == "premise-refuted":
        require_nonempty(row.get("refutation_scope"), f"{label}.refutation_scope", errors)
    if "post_lock_exception" in row:
        errors.append(f"{label}.post_lock_exception: exceptions must be top-level records")
    validate_amendments(row, label, repo_root, head_sha, captured_at, errors)


def validate_ledger(payload: Any, repo_root: Path) -> list[str]:  # noqa: C901, PLR0915
    """Return structural violations; never judge issue prose or GitHub freshness."""
    errors: list[str] = []
    root = require_mapping(payload, "ledger", errors)
    required = ("schema_version", "repo", "captured_at", "head_sha", "issue_count", "list_truncated", "activation_issue_snapshot", "release_planner_receipt", "quality_planner_receipt", "issue_plan_receipt", "issues", "work_packages", "parent_only_paths", "post_lock_exceptions", "freshness_note")
    for key in required:
        if key not in root:
            errors.append(f"ledger.{key}: required")
    if root.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"ledger.schema_version: expected {SCHEMA_VERSION!r}")
    if root.get("repo") != REPOSITORY:
        errors.append(f"ledger.repo: expected {REPOSITORY!r}")
    captured_at = parse_timestamp(root.get("captured_at"), "ledger.captured_at", errors)
    head_sha = root.get("head_sha")
    if not isinstance(head_sha, str) or not (HEX40.fullmatch(head_sha) or HEX64.fullmatch(head_sha)):
        errors.append("ledger.head_sha: commit SHA required")
    if root.get("list_truncated") is not False:
        errors.append("ledger.list_truncated: activation snapshot must be non-truncated")
    if not isinstance(root.get("issue_count"), int) or isinstance(root.get("issue_count"), bool):
        errors.append("ledger.issue_count: integer required")
    issues = root.get("issues") if isinstance(root.get("issues"), list) else []
    if isinstance(root.get("issues"), list) and root.get("issue_count") != len(issues):
        errors.append("ledger.issue_count: does not equal issues length")
    snapshot = require_mapping(root.get("activation_issue_snapshot"), "ledger.activation_issue_snapshot", errors)
    numbers = validate_snapshot(repo_root, snapshot, errors)
    if len(set(numbers)) != len(numbers):
        errors.append("ledger.activation_issue_snapshot.numbers: duplicate issue number")
    note = root.get("freshness_note")
    if not isinstance(note, str) or "GitHub freshness is re-read" not in note:
        errors.append("ledger.freshness_note: must say GitHub freshness is re-read")
    for key in ("release_planner_receipt", "quality_planner_receipt", "issue_plan_receipt"):
        validate_receipt(repo_root, root.get(key), f"ledger.{key}", head_sha, errors)
    seen: set[int] = set()
    for index, issue in enumerate(issues):
        validate_issue(repo_root, issue, index, head_sha, captured_at, errors)
        if isinstance(issue, dict) and isinstance(issue.get("number"), int) and not isinstance(issue.get("number"), bool):
            number = issue["number"]
            if number in seen:
                errors.append(f"issues[{index}].number: duplicate activation issue")
            seen.add(number)
    if seen != set(numbers):
        errors.append(f"issues: exactly-once activation coverage mismatch (missing={sorted(set(numbers) - seen)}, extra={sorted(seen - set(numbers))})")
    parent_only = root.get("parent_only_paths")
    if not isinstance(parent_only, list) or not all(isinstance(path, str) and path.strip() for path in parent_only):
        errors.append("ledger.parent_only_paths: non-empty string list required")
        parent_only = []
    else:
        for index, path in enumerate(parent_only):
            repo_path(repo_root, path, field=f"ledger.parent_only_paths[{index}]", errors=errors)
    issue_rows = {issue.get("number"): issue for issue in issues if isinstance(issue, dict) and isinstance(issue.get("number"), int) and not isinstance(issue.get("number"), bool)}
    issue_footprints: list[tuple[int, str]] = []
    for number, issue in issue_rows.items():
        for path in issue.get("allowed_paths") or []:
            if not isinstance(path, str):
                continue
            if any(path == parent or path.startswith(parent.rstrip("/") + "/") for parent in parent_only):
                errors.append(f"issues[{number}].allowed_paths: parent-only path admitted: {path}")
            if issue.get("classification") in {"qualified-repair", "release-blocker"}:
                for prior_number, prior_path in issue_footprints:
                    if path_overlaps(path, prior_path):
                        errors.append(f"issues[{number}].allowed_paths: overlaps issue #{prior_number}:{prior_path}")
                issue_footprints.append((number, path))
    packages = root.get("work_packages") if isinstance(root.get("work_packages"), list) else []
    package_ids: set[str] = set()
    footprints: list[tuple[str, str]] = []
    for index, package in enumerate(packages):
        label = f"work_packages[{index}]"
        row = require_mapping(package, label, errors)
        package_id = row.get("package_id")
        if not isinstance(package_id, str) or not package_id.strip() or package_id in package_ids:
            errors.append(f"{label}.package_id: unique non-empty id required")
        package_ids.add(str(package_id))
        issue_numbers = row.get("issue_numbers")
        require_string_list([str(n) for n in issue_numbers] if isinstance(issue_numbers, list) and all(isinstance(n, int) and not isinstance(n, bool) for n in issue_numbers) else issue_numbers, f"{label}.issue_numbers", errors, nonempty=True)
        if not isinstance(issue_numbers, list) or any(not isinstance(number, int) or isinstance(number, bool) or number not in seen for number in issue_numbers):
            errors.append(f"{label}.issue_numbers: references only non-boolean activation issue numbers")
        require_nonempty(row.get("lane_id"), f"{label}.lane_id", errors)
        require_nonempty(row.get("status"), f"{label}.status", errors)
        paths = row.get("allowed_paths")
        require_string_list(paths, f"{label}.allowed_paths", errors, nonempty=True)
        authorized = [allowed for number in issue_numbers if isinstance(issue_numbers, list) for allowed in (issue_rows.get(number, {}).get("allowed_paths") or []) if isinstance(allowed, str)]
        for path in paths if isinstance(paths, list) else []:
            repo_path(repo_root, path, field=f"{label}.allowed_paths", errors=errors)
            if not any(path_within_budget(path, allowed) for allowed in authorized):
                errors.append(f"{label}.allowed_paths: path is outside every referenced issue budget: {path}")
            if any(path == parent or path.startswith(parent.rstrip("/") + "/") for parent in parent_only):
                errors.append(f"{label}.allowed_paths: parent-only path admitted: {path}")
            for prior_package, prior_path in footprints:
                if path_overlaps(path, prior_path):
                    errors.append(f"{label}.allowed_paths: overlaps {prior_package}:{prior_path}; declare a serialized/shared lane")
            footprints.append((str(package_id), path))
        require_string_list(row.get("dependencies"), f"{label}.dependencies", errors)
        proof_commands = row.get("proof_commands")
        require_string_list(proof_commands, f"{label}.proof_commands", errors)
        required_proofs = {
            command
            for number in issue_numbers
            if isinstance(issue_numbers, list)
            for command in (issue_rows.get(number, {}).get("proof_commands") or [])
            if isinstance(command, str)
        }
        if isinstance(proof_commands, list):
            missing_proofs = sorted(required_proofs - set(proof_commands))
            if missing_proofs:
                errors.append(
                    f"{label}.proof_commands: missing issue acceptance command(s): "
                    + "; ".join(missing_proofs)
                )
    qualified = {issue.get("number") for issue in issues if isinstance(issue, dict) and issue.get("classification") in {"qualified-repair", "release-blocker"}}
    packaged = {number for package in packages if isinstance(package, dict) for number in package.get("issue_numbers", [])}
    for number in sorted(qualified - packaged):
        errors.append(f"issue #{number}: qualified disposition has no work package")
    validate_post_lock_exceptions(repo_root, root.get("post_lock_exceptions"), set(numbers), head_sha, captured_at, errors)
    return errors


def summary(payload: dict[str, Any]) -> dict[str, Any]:
    counts = Counter(issue["classification"] for issue in payload["issues"])
    return {"status": "pass", "schema_version": SCHEMA_VERSION, "issue_count": len(payload["issues"]), "classification_counts": dict(sorted(counts.items())), "work_package_count": len(payload["work_packages"]), "note": "GitHub freshness is re-read before issue closeout and publication; this gate validates the captured snapshot only."}
