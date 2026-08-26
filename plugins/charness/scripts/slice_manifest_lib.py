"""Validate the identity record shared by post-push proof slices.

This module deliberately validates captured evidence offline.  It never asks
GitHub for current state and never executes a command named by the manifest.
Those are separate observer-owned operations in later slices.
"""

from __future__ import annotations

import ast
import hashlib
import json
import re
import subprocess
from pathlib import Path, PurePosixPath
from typing import Any

from scripts.goal_lineage import (
    LineageError,
    load_goal_lineage_file,
    not_goal_bound_lineage,
    require_goal_execution_identity,
    validate_goal_lineage,
    verify_goal_lineage_references,
)

SCHEMA_VERSION = 1
MANIFEST_KIND = "charness.slice-manifest"
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
GIT_SHA_RE = re.compile(r"^[0-9a-f]{40}$")
ALLOWED_RELATIONS = {"equals_target"}
ALLOWED_READER_ROLES = {"source", "plugin", "consumer", "owner"}


class ManifestError(ValueError):
    """A deterministic manifest refusal with a machine-readable code."""

    def __init__(self, code: str, path: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.path = path

    def as_dict(self) -> dict[str, str]:
        return {"code": self.code, "path": self.path, "message": str(self)}


def _error(code: str, path: str, message: str) -> None:
    raise ManifestError(code, path, message)


def _require_mapping(value: Any, path: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        _error("invalid_type", path, "expected an object")
    return value


def _require_string(value: Any, path: str) -> str:
    if not isinstance(value, str) or not value.strip():
        _error("invalid_type", path, "expected a non-empty string")
    return value


def _require_int(value: Any, path: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        _error("invalid_type", path, "expected an integer")
    return value


def _require_sha(value: Any, path: str, *, kind: str = "git") -> str:
    candidate = _require_string(value, path)
    expression = GIT_SHA_RE if kind == "git" else SHA256_RE
    if expression.fullmatch(candidate) is None:
        expected = "40 lowercase hexadecimal characters" if kind == "git" else "64 lowercase hexadecimal characters"
        _error("invalid_identity", path, f"expected {expected}; got `{candidate}`")
    return candidate


def _safe_repo_path(value: Any, path: str) -> str:
    candidate = _require_string(value, path)
    if "\\" in candidate:
        _error("unsafe_path", path, "use a repo-relative POSIX path, not a backslash path")
    parsed = PurePosixPath(candidate)
    if parsed.is_absolute() or ".." in parsed.parts or "." in parsed.parts:
        _error("unsafe_path", path, "path must be relative and must not contain `.` or `..`")
    if candidate.endswith("/"):
        _error("unsafe_path", path, "path must not have a trailing slash")
    return candidate


def _repo_candidate(repo_root: Path, relative: str, path: str) -> Path:
    candidate = repo_root / relative
    try:
        resolved = candidate.resolve()
        resolved.relative_to(repo_root.resolve())
    except ValueError:
        _error("unsafe_path", path, "path resolves outside the repository")
    return candidate


def _require_repo_entry(repo_root: Path, relative: str, path: str, *, file_only: bool = False) -> Path:
    candidate = _repo_candidate(repo_root, relative, path)
    if not candidate.exists():
        _error("missing_path", path, f"declared path does not exist: `{relative}`")
    if file_only and not candidate.is_file():
        _error("invalid_root", path, f"declared identity path is not a file: `{relative}`")
    return candidate


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _git(repo_root: Path, *args: str) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(["git", *args], cwd=repo_root, capture_output=True, check=False)


def _require_git_commit(repo_root: Path, sha: str, path: str) -> None:
    result = _git(repo_root, "cat-file", "-e", f"{sha}^{{commit}}")
    if result.returncode != 0:
        _error("missing_git_object", path, f"git commit object is not available: `{sha}`")


def _validate_owner_ref(repo_root: Path, value: Any, path: str) -> None:
    owner = _require_string(value, path)
    if "#" not in owner:
        _error("invalid_owner", path, "owner reference must include a file anchor after `#`")
    owner_path, anchor = owner.split("#", 1)
    if not owner_path:
        _error("invalid_owner", path, "owner reference must name a repository file")
    if not anchor.strip() or any(char.isspace() for char in anchor):
        _error("invalid_owner", path, "owner reference must name a non-empty anchor without whitespace")
    _safe_repo_path(owner_path, path)
    owner_file = _require_repo_entry(repo_root, owner_path, path, file_only=True)
    if owner_path.endswith(".json"):
        try:
            anchored_value: Any = json.loads(owner_file.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            _error("invalid_owner", path, f"owner JSON cannot be read: {exc}")
        for key in anchor.split("."):
            if not isinstance(anchored_value, dict) or key not in anchored_value:
                _error("invalid_owner", path, f"owner JSON anchor does not exist: `{anchor}`")
            anchored_value = anchored_value[key]
        return
    if owner_path.endswith(".py"):
        try:
            tree = ast.parse(owner_file.read_text(encoding="utf-8"), filename=owner_path)
        except (OSError, UnicodeError, SyntaxError) as exc:
            _error("invalid_owner", path, f"owner Python source cannot be parsed: {exc}")
        if not any(
            isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and node.name == anchor
            for node in tree.body
        ):
            _error("invalid_owner", path, f"owner Python anchor does not exist: `{anchor}`")
        return
    _error("invalid_owner", path, f"owner anchor validation is unsupported for `{owner_path}`")


def _validate_observation(
    repo_root: Path,
    observation: Any,
    path: str,
    target_sha: str,
    repository: str,
    remote_ref: str,
) -> None:
    data = _require_mapping(observation, path)
    if data.get("status") != "captured":
        _error("uncaptured_evidence", f"{path}.status", "remote evidence must be explicitly marked `captured`")
    _require_string(data.get("channel"), f"{path}.channel")
    _require_string(data.get("observed_at"), f"{path}.observed_at")
    observed_repository = _require_string(data.get("repository"), f"{path}.repository")
    observed_ref = _require_string(data.get("ref"), f"{path}.ref")
    if observed_repository != repository:
        _error("identity_mismatch", f"{path}.repository", f"expected `{repository}`, got `{observed_repository}`")
    if observed_ref != remote_ref:
        _error("identity_mismatch", f"{path}.ref", f"expected `{remote_ref}`, got `{observed_ref}`")
    observed_sha = _require_sha(data.get("sha"), f"{path}.sha")
    if observed_sha != target_sha:
        _error("identity_mismatch", f"{path}.sha", f"expected target SHA `{target_sha}`, got `{observed_sha}`")
    command = data.get("command")
    if not isinstance(command, list) or not command or not all(isinstance(item, str) and item for item in command):
        _error("invalid_command_descriptor", f"{path}.command", "expected a non-empty argv array of strings")


def _validate_reader_roots(repo_root: Path, data: Any, *, verify_current: bool) -> list[dict[str, Any]]:
    roots = data
    if not isinstance(roots, list) or not roots:
        _error("invalid_reader_roots", "reader_roots", "expected a non-empty array")
    seen_ids: set[str] = set()
    seen_identity_paths: set[str] = set()
    for index, raw_root in enumerate(roots):
        path = f"reader_roots[{index}]"
        root = _require_mapping(raw_root, path)
        root_id = _require_string(root.get("id"), f"{path}.id")
        if root_id in seen_ids:
            _error("duplicate_reader_root", f"{path}.id", f"reader root id already declared: `{root_id}`")
        seen_ids.add(root_id)
        role = _require_string(root.get("role"), f"{path}.role")
        if role not in ALLOWED_READER_ROLES:
            _error("invalid_reader_role", f"{path}.role", f"unsupported reader role `{role}`")
        root_path = _safe_repo_path(root.get("path"), f"{path}.path")
        identity_mode = _require_string(root.get("identity_mode"), f"{path}.identity_mode")
        if identity_mode not in {"captured", "current"}:
            _error("invalid_reader_root", f"{path}.identity_mode", "expected `captured` or `current`")
        if verify_current or identity_mode == "current":
            _require_repo_entry(repo_root, root_path, f"{path}.path")
        _validate_owner_ref(repo_root, root.get("owner"), f"{path}.owner")
        identity_paths = root.get("identity_paths")
        if not isinstance(identity_paths, list) or not identity_paths:
            _error("invalid_reader_root", f"{path}.identity_paths", "declare at least one concrete identity file")
        for path_index, raw_identity_path in enumerate(identity_paths):
            identity_path = _safe_repo_path(raw_identity_path, f"{path}.identity_paths[{path_index}]")
            if identity_path in seen_identity_paths:
                _error("duplicate_identity_path", f"{path}.identity_paths[{path_index}]", f"path already declared: `{identity_path}`")
            seen_identity_paths.add(identity_path)
            if verify_current or identity_mode == "current":
                _require_repo_entry(repo_root, identity_path, f"{path}.identity_paths[{path_index}]", file_only=True)
        declared_digest = _require_sha(root.get("identity_sha256"), f"{path}.identity_sha256", kind="sha256")
        if verify_current or identity_mode == "current":
            actual_digest = _root_identity_digest(repo_root, [str(value) for value in identity_paths])
            if actual_digest != declared_digest:
                _error("stale_reader_root", f"{path}.identity_sha256", f"expected `{declared_digest}`, current identity is `{actual_digest}`")
    return roots


def _root_identity_digest(repo_root: Path, paths: list[str]) -> str:
    entries = []
    for relative in sorted(paths):
        candidate = _require_repo_entry(repo_root, relative, f"reader_roots.identity_paths[{relative}]", file_only=True)
        entries.append({"path": relative, "sha256": _sha256_file(candidate)})
    canonical = json.dumps(entries, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _validate_parity(repo_root: Path, pairs: Any, *, verify_current: bool) -> None:
    if not isinstance(pairs, list) or not pairs:
        _error("invalid_parity", "parity_pairs", "expected a non-empty array")
    for index, raw_pair in enumerate(pairs):
        path = f"parity_pairs[{index}]"
        pair = _require_mapping(raw_pair, path)
        source = _safe_repo_path(pair.get("source"), f"{path}.source")
        derived = _safe_repo_path(pair.get("derived"), f"{path}.derived")
        mode = _require_string(pair.get("identity_mode"), f"{path}.identity_mode")
        if mode not in {"captured", "current"}:
            _error("invalid_parity", f"{path}.identity_mode", "expected `captured` or `current`")
        source_sha = _require_sha(pair.get("source_sha256"), f"{path}.source_sha256", kind="sha256")
        derived_sha = _require_sha(pair.get("derived_sha256"), f"{path}.derived_sha256", kind="sha256")
        if verify_current or mode == "current":
            source_path = _require_repo_entry(repo_root, source, f"{path}.source", file_only=True)
            derived_path = _require_repo_entry(repo_root, derived, f"{path}.derived", file_only=True)
            actual_source_sha = _sha256_file(source_path)
            actual_derived_sha = _sha256_file(derived_path)
            if actual_source_sha != source_sha or actual_derived_sha != derived_sha or source_path.read_bytes() != derived_path.read_bytes():
                _error("parity_mismatch", path, f"source `{source}` and derived `{derived}` are not byte-identical")


def _validate_ci_readback(data: Any, target_sha: str, repository: str, remote_ref: str) -> None:
    proof = _require_mapping(data, "ci_readback")
    if proof.get("status") != "captured":
        _error("uncaptured_evidence", "ci_readback.status", "CI readback must be explicitly marked `captured`")
    _require_string(proof.get("channel"), "ci_readback.channel")
    non_claim = _require_string(proof.get("non_claim"), "ci_readback.non_claim")
    if "runtime behavior" not in non_claim or "not claimed" not in non_claim:
        _error("invalid_ci_readback", "ci_readback.non_claim", "CI readback must state that runtime behavior is not claimed")
    if _require_string(proof.get("repository"), "ci_readback.repository") != repository:
        _error("identity_mismatch", "ci_readback.repository", f"expected `{repository}`")
    if _require_string(proof.get("remote_ref"), "ci_readback.remote_ref") != remote_ref:
        _error("identity_mismatch", "ci_readback.remote_ref", f"expected `{remote_ref}`")
    head_sha = _require_sha(proof.get("head_sha"), "ci_readback.head_sha")
    if head_sha != target_sha:
        _error("identity_mismatch", "ci_readback.head_sha", f"expected target SHA `{target_sha}`, got `{head_sha}`")
    run_id = _require_int(proof.get("run_id"), "ci_readback.run_id")
    if run_id <= 0:
        _error("invalid_ci_readback", "ci_readback.run_id", "run id must be positive")
    if proof.get("conclusion") != "success":
        _error("unsuccessful_ci_readback", "ci_readback.conclusion", "captured CI readback must be completed successfully")
    jobs = proof.get("jobs")
    if not isinstance(jobs, list) or not jobs:
        _error("incomplete_ci_readback", "ci_readback.jobs", "at least one completed job is required")
    for index, raw_job in enumerate(jobs):
        job_path = f"ci_readback.jobs[{index}]"
        job = _require_mapping(raw_job, job_path)
        job_id = _require_int(job.get("id"), f"{job_path}.id")
        if job_id <= 0:
            _error("invalid_ci_readback", f"{job_path}.id", "job id must be positive")
        job_sha = _require_sha(job.get("head_sha"), f"{job_path}.head_sha")
        if job_sha != target_sha:
            _error("identity_mismatch", f"{job_path}.head_sha", f"expected target SHA `{target_sha}`, got `{job_sha}`")
        if job.get("status") != "completed" or job.get("conclusion") != "success":
            _error("incomplete_ci_readback", job_path, "every recorded job must be completed successfully")


def _validate_remote_target_identity(data: dict[str, Any], path: str, target_sha: str, repository: str, remote_ref: str) -> None:
    if _require_string(data.get("repository"), f"{path}.repository") != repository:
        _error("identity_mismatch", f"{path}.repository", f"expected `{repository}`")
    if _require_string(data.get("remote_ref"), f"{path}.remote_ref") != remote_ref:
        _error("identity_mismatch", f"{path}.remote_ref", f"expected `{remote_ref}`")
    if _require_sha(data.get("target_sha"), f"{path}.target_sha") != target_sha:
        _error("identity_mismatch", f"{path}.target_sha", f"expected target SHA `{target_sha}`")


def _validate_issue_readback(data: Any, target_sha: str, repository: str, remote_ref: str) -> None:
    readback = _require_mapping(data, "remote_readback.open_issues")
    if readback.get("status") != "captured":
        _error("uncaptured_evidence", "remote_readback.open_issues.status", "issue state must be an explicitly captured readback")
    _require_string(readback.get("channel"), "remote_readback.open_issues.channel")
    _require_string(readback.get("observed_at"), "remote_readback.open_issues.observed_at")
    _validate_remote_target_identity(readback, "remote_readback.open_issues", target_sha, repository, remote_ref)
    query = readback.get("query")
    if not isinstance(query, list) or not query or not all(isinstance(item, str) and item for item in query):
        _error("invalid_command_descriptor", "remote_readback.open_issues.query", "expected a non-empty argv array of strings")
    open_count = _require_int(readback.get("open_count"), "remote_readback.open_issues.open_count")
    if open_count < 0:
        _error("invalid_readback", "remote_readback.open_issues.open_count", "open issue count cannot be negative")


def _validate_critique(repo_root: Path, data: Any, *, verify_current: bool) -> None:
    critique = _require_mapping(data, "critique")
    artifact_path = _safe_repo_path(critique.get("artifact_path"), "critique.artifact_path")
    packet_path = _safe_repo_path(critique.get("packet_path"), "critique.packet_path")
    if artifact_path != packet_path:
        _error("unbound_critique", "critique.packet_path", "Slice 1 requires the durable review artifact to be the bound packet")
    artifact = _require_repo_entry(repo_root, artifact_path, "critique.artifact_path", file_only=True)
    expected_packet_sha = _require_sha(critique.get("packet_sha256"), "critique.packet_sha256", kind="sha256")
    expected_reviewed_packet_sha = _require_sha(critique.get("reviewed_packet_sha256"), "critique.reviewed_packet_sha256", kind="sha256")
    expected_identity = _require_sha(critique.get("reviewed_identity_sha256"), "critique.reviewed_identity_sha256", kind="sha256")
    if verify_current:
        actual_packet_sha = _sha256_file(artifact)
        if expected_packet_sha != actual_packet_sha:
            _error("stale_critique_packet", "critique.packet_sha256", f"expected `{expected_packet_sha}`, current packet is `{actual_packet_sha}`")
        try:
            text = artifact.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            _error("unbound_critique", "critique.artifact_path", f"durable critique packet cannot be read: {exc}")
        identity_marker = re.compile(rf'"identity_sha256"\s*:\s*"{re.escape(expected_identity)}"')
        packet_marker = re.compile(rf'"packet_sha256"\s*:\s*"{re.escape(expected_reviewed_packet_sha)}"')
        if identity_marker.search(text) is None or packet_marker.search(text) is None:
            _error("unbound_critique", "critique.reviewed_identity_sha256", "durable critique packet does not declare the bound packet identity record")
    if critique.get("status") != "captured":
        _error("uncaptured_evidence", "critique.status", "critique evidence must be explicitly marked `captured`")


def _load_manifest(repo_root: Path, manifest_path: Path) -> dict[str, Any]:
    try:
        manifest_path.resolve().relative_to(repo_root.resolve())
    except ValueError:
        _error("unsafe_path", "manifest", "manifest must be inside the repository")
    if not manifest_path.exists():
        _error("missing_manifest", "manifest", f"manifest does not exist: `{manifest_path}`")
    if not manifest_path.is_file():
        _error("invalid_manifest_path", "manifest", f"manifest path is not a file: `{manifest_path}`")
    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        _error("invalid_json", "manifest", f"manifest is not valid JSON: {exc.msg}")
    except UnicodeError as exc:
        _error("invalid_json", "manifest", f"manifest is not valid UTF-8: {exc}")
    _require_mapping(data, "manifest")
    return data


def _validate_target_and_premise(repo_root: Path, data: dict[str, Any], repository: str) -> tuple[str, str, str]:
    target = _require_mapping(data.get("target"), "target")
    target_sha = _require_sha(target.get("sha"), "target.sha")
    _require_git_commit(repo_root, target_sha, "target.sha")
    _require_string(target.get("ref"), "target.ref")
    remote_ref = _require_string(target.get("remote_ref"), "target.remote_ref")
    if _require_string(target.get("remote_repository"), "target.remote_repository") != repository:
        _error("identity_mismatch", "target.remote_repository", f"expected `{repository}`")
    if target.get("kind") != "published-baseline":
        _error("invalid_target", "target.kind", "Slice 1 target must be a published baseline")

    carrier = _require_mapping(data.get("carrier"), "carrier")
    carrier_sha = _require_sha(carrier.get("sha"), "carrier.sha")
    if carrier.get("relation_to_target") not in ALLOWED_RELATIONS:
        _error("invalid_carrier_relation", "carrier.relation_to_target", "Slice 1 only supports `equals_target`")
    if carrier_sha != target_sha:
        _error("identity_mismatch", "carrier.sha", f"expected target SHA `{target_sha}`, got `{carrier_sha}`")
    _require_git_commit(repo_root, carrier_sha, "carrier.sha")

    premise = _require_mapping(data.get("premise"), "premise")
    if premise.get("status") != "captured":
        _error("uncaptured_evidence", "premise.status", "premise must be explicitly marked `captured`")
    _require_sha(premise.get("published_target_sha"), "premise.published_target_sha")
    if premise["published_target_sha"] != target_sha:
        _error("identity_mismatch", "premise.published_target_sha", "premise target does not match target.sha")
    local_head_sha = _require_sha(premise.get("local_head_sha"), "premise.local_head_sha")
    _require_git_commit(repo_root, local_head_sha, "premise.local_head_sha")
    ancestor_check = _git(repo_root, "merge-base", "--is-ancestor", target_sha, local_head_sha)
    if ancestor_check.returncode != 0:
        _error("identity_mismatch", "premise.local_head_sha", "local capture head is not at or after the published target")
    _validate_observation(repo_root, premise.get("remote_observation"), "premise.remote_observation", target_sha, repository, remote_ref)
    return target_sha, carrier_sha, remote_ref


def _validate_remote_readbacks(data: dict[str, Any], target_sha: str, repository: str, remote_ref: str) -> int:
    _validate_ci_readback(data.get("ci_readback"), target_sha, repository, remote_ref)
    remote_readback = _require_mapping(data.get("remote_readback"), "remote_readback")
    if remote_readback.get("actions_run_id") != data["ci_readback"]["run_id"]:
        _error("identity_mismatch", "remote_readback.actions_run_id", "remote Actions run must match ci_readback.run_id")
    _validate_remote_target_identity(remote_readback, "remote_readback", target_sha, repository, remote_ref)
    _validate_issue_readback(remote_readback.get("open_issues"), target_sha, repository, remote_ref)
    return remote_readback["open_issues"]["open_count"]


def _manifest_lineage(
    repo_root: Path,
    data: dict[str, Any],
    *,
    goal_lineage_path: Path | None,
) -> dict[str, Any]:
    try:
        if goal_lineage_path is not None:
            if data.get("goal_lineage") is not None:
                _error("lineage_mismatch", "goal_lineage", "use either embedded goal_lineage or --goal-lineage-file, not both")
            return require_goal_execution_identity(
                load_goal_lineage_file(repo_root, goal_lineage_path)
            )
        if data.get("goal_lineage") is None:
            return not_goal_bound_lineage("slice manifest was captured without a Goal Run Work Item identity")
        return verify_goal_lineage_references(repo_root, validate_goal_lineage(data["goal_lineage"], repo_root=repo_root))
    except LineageError as exc:
        _error("invalid_lineage", "goal_lineage", str(exc))
    raise AssertionError("unreachable")


def validate_manifest(
    repo_root: Path,
    manifest_path: Path,
    *,
    verify_current: bool = False,
    goal_lineage_path: Path | None = None,
) -> dict[str, Any]:
    data = _load_manifest(repo_root, manifest_path)
    if data.get("kind") != MANIFEST_KIND:
        _error("invalid_kind", "kind", f"expected `{MANIFEST_KIND}`")
    if data.get("schema_version") != SCHEMA_VERSION:
        _error("unsupported_schema", "schema_version", f"expected schema version {SCHEMA_VERSION}")
    _require_string(data.get("slice_id"), "slice_id")
    captured_at = _require_string(data.get("captured_at"), "captured_at")
    if not captured_at.endswith("Z"):
        _error("invalid_timestamp", "captured_at", "captured_at must be an RFC3339 UTC timestamp ending in `Z`")
    repository = _require_string(data.get("repository"), "repository")
    goal_path = _safe_repo_path(data.get("goal_path"), "goal_path")
    _require_repo_entry(repo_root, goal_path, "goal_path", file_only=True)
    goal_lineage = _manifest_lineage(repo_root, data, goal_lineage_path=goal_lineage_path)
    if goal_lineage["disposition"] == "goal-bound" and goal_lineage["work_item"]["repo"] != repository:
        _error("lineage_mismatch", "goal_lineage.work_item.repo", f"expected `{repository}`")
    target_sha, carrier_sha, remote_ref = _validate_target_and_premise(repo_root, data, repository)
    open_issue_count = _validate_remote_readbacks(data, target_sha, repository, remote_ref)

    _validate_critique(repo_root, data.get("critique"), verify_current=verify_current)

    _validate_reader_roots(repo_root, data.get("reader_roots"), verify_current=verify_current)
    _validate_parity(repo_root, data.get("parity_pairs"), verify_current=verify_current)
    return {
        "status": "structurally-valid-captured-record",
        "kind": data["kind"],
        "schema_version": data["schema_version"],
        "slice_id": data["slice_id"],
        "target_sha": target_sha,
        "carrier_sha": carrier_sha,
        "ci_run_id": data["ci_readback"]["run_id"],
        "captured_open_issue_count": open_issue_count,
        "live_revalidation": "not-run",
        "reader_root_count": len(data["reader_roots"]),
        "parity_pair_count": len(data["parity_pairs"]),
        "goal_lineage": goal_lineage,
    }
