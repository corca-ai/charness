"""Strict, file-backed inputs for the guarded Goal Run close ingress."""

from __future__ import annotations

import hashlib
import json
import runpy
from pathlib import Path
from typing import Any

_load_local = runpy.run_path(str(Path(__file__).resolve().parent / "issue_local_import.py"))[
    "sibling_loader"
](__file__)
INPUT = _load_local("issue_goal_run_input", "issue_goal_run_close_contract_input")
GoalRunInputError = INPUT.GoalRunInputError

CLOSE_PROOF_KIND = "charness.goal-run-close-proof/v1"
FINAL_PROOF_INDEX_KIND = "charness.goal-run-final-proof-index/v1"


def _bound_json_file(
    repo_root: Path,
    value: Any,
    declared_sha256: Any,
    *,
    kind: str,
    context: str,
) -> tuple[Path, dict[str, Any], str]:
    path = INPUT.repo_file(repo_root, value, context=f"{context}_file")
    expected = INPUT.sha(declared_sha256, f"{context}_sha256")
    raw = path.read_bytes()
    actual = hashlib.sha256(raw).hexdigest()
    if actual != expected:
        raise INPUT.error(
            "input-stale",
            f"{context} bytes do not match its declared SHA-256: expected {expected}, got {actual}",
        )
    try:
        payload = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise INPUT.error("input-invalid", f"{context} is not canonical UTF-8 JSON: {exc}") from exc
    if not isinstance(payload, dict):
        raise INPUT.error("schema-invalid", f"{context} must contain a JSON object")
    if payload.get("kind") != kind:
        raise INPUT.error("schema-unknown", f"{context}.kind must be {kind}")
    return path, payload, actual


def _bound_file(
    repo_root: Path, value: Any, declared_sha256: Any, *, context: str
) -> tuple[Path, str]:
    path = INPUT.repo_file(repo_root, value, context=f"{context}.path")
    expected = INPUT.sha(declared_sha256, f"{context}.sha256")
    actual = hashlib.sha256(path.read_bytes()).hexdigest()
    if actual != expected:
        raise INPUT.error(
            "input-stale",
            f"{context} bytes do not match its declared SHA-256: expected {expected}, got {actual}",
        )
    return path, actual


def _reference(value: Any, *, context: str) -> tuple[str, str]:
    if not isinstance(value, dict):
        raise INPUT.error("schema-invalid", f"{context} must be an object")
    INPUT.fields(value, {"path", "sha256"}, context)
    path = value.get("path")
    if not isinstance(path, str) or not path.strip():
        raise INPUT.error("path-invalid", f"{context}.path must be non-empty text")
    return path, INPUT.sha(value.get("sha256"), f"{context}.sha256")


def _load_expected_children(
    repo_root: Path, value: Any, *, repo: str, parent_number: int
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    path_value, digest = _reference(value, context="final proof index.expected_children")
    path, payload, _ = _bound_json_file(
        repo_root,
        path_value,
        digest,
        kind="charness.expected-sub-issue-set/v1",
        context="expected_children",
    )
    INPUT.fields(payload, {"kind", "repo", "parent_number", "children", "source"}, "expected child set")
    if INPUT.repo(payload.get("repo"), "expected child set.repo").lower() != repo.lower():
        raise INPUT.error("parent-mismatch", "expected child set repository differs from the Goal Run")
    if INPUT.positive(payload.get("parent_number"), "expected child set.parent_number") != parent_number:
        raise INPUT.error("parent-mismatch", "expected child set parent differs from the Goal Run")
    numbers = payload.get("children")
    if not isinstance(numbers, list) or any(type(number) is not int or number <= 0 for number in numbers):
        raise INPUT.error("proof-incomplete", "expected child set must list positive issue numbers")
    if len(numbers) != len(set(numbers)) or parent_number in numbers:
        raise INPUT.error("proof-incomplete", "expected child set contains a duplicate or the parent")
    children = [{"repo": repo, "number": number} for number in sorted(numbers)]
    return children, {"path": str(path), "sha256": digest}


def _load_evidence(repo_root: Path, value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list) or not value:
        raise INPUT.error("proof-incomplete", "final proof index must bind at least one evidence artifact")
    evidence: list[dict[str, Any]] = []
    seen_roles: set[str] = set()
    for index, item in enumerate(value):
        context = f"final proof index.evidence[{index}]"
        if not isinstance(item, dict):
            raise INPUT.error("schema-invalid", f"{context} must be an object")
        INPUT.fields(item, {"role", "path", "sha256"}, context)
        role = item.get("role")
        if not isinstance(role, str) or not role.strip() or len(role) > 128:
            raise INPUT.error("schema-invalid", f"{context}.role must be bounded non-empty text")
        if role in seen_roles:
            raise INPUT.error("proof-incomplete", f"final proof index repeats evidence role {role!r}")
        seen_roles.add(role)
        path, digest = _bound_file(repo_root, item.get("path"), item.get("sha256"), context=context)
        evidence.append({"role": role, "path": str(path), "sha256": digest})
    return evidence


def load_final_proof_index(
    path: Path,
    *,
    repo_root: Path,
    repo: str,
    parent_number: int,
    draft_sha256: str,
    binding_sha256: str,
    sha256: str,
) -> dict[str, Any]:
    path, value, digest = _bound_json_file(
        repo_root,
        str(path),
        sha256,
        kind=FINAL_PROOF_INDEX_KIND,
        context="final_proof_index",
    )
    INPUT.fields(
        value,
        {
            "kind",
            "repo",
            "parent_number",
            "draft_sha256",
            "binding_sha256",
            "expected_children",
            "parent_obligation",
            "evidence",
        },
        "final proof index",
    )
    if INPUT.repo(value.get("repo"), "final proof index.repo").lower() != repo.lower():
        raise INPUT.error(
            "parent-mismatch", "final proof index repository differs from the requested repository"
        )
    if INPUT.positive(value.get("parent_number"), "final proof index.parent_number") != parent_number:
        raise INPUT.error("parent-mismatch", "final proof index parent differs from the requested parent")
    if INPUT.sha(value.get("draft_sha256"), "final proof index.draft_sha256") != draft_sha256:
        raise INPUT.error("input-stale", "final proof index draft hash differs from the close proof")
    if INPUT.sha(value.get("binding_sha256"), "final proof index.binding_sha256") != binding_sha256:
        raise INPUT.error("input-stale", "final proof index binding hash differs from the close proof")

    children, expected_children = _load_expected_children(
        repo_root, value.get("expected_children"), repo=repo, parent_number=parent_number
    )
    obligation_path, obligation_digest = _reference(
        value.get("parent_obligation"), context="final proof index.parent_obligation"
    )
    obligation_path, _ = _bound_file(
        repo_root,
        obligation_path,
        obligation_digest,
        context="final proof index.parent_obligation",
    )
    try:
        obligation_text = obligation_path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise INPUT.error("input-invalid", "parent obligation is not valid UTF-8 text") from exc
    if not obligation_text.strip():
        raise INPUT.error("proof-incomplete", "parent obligation must not be empty")
    evidence = _load_evidence(repo_root, value.get("evidence"))
    return {
        "path": str(path),
        "sha256": digest,
        "kind": FINAL_PROOF_INDEX_KIND,
        "repo": repo,
        "parent_number": parent_number,
        "draft_sha256": draft_sha256,
        "binding_sha256": binding_sha256,
        "expected_children": children,
        "expected_children_source": expected_children,
        "parent_obligation": {"path": str(obligation_path), "sha256": obligation_digest},
        "evidence": evidence,
    }


def _validate_children(value: Any, *, repo: str) -> list[dict[str, Any]]:
    if not isinstance(value, list) or not value:
        raise INPUT.error("proof-incomplete", "close proof must list every linked child")
    seen_children: set[tuple[str, int]] = set()
    for index, child in enumerate(value):
        if not isinstance(child, dict):
            raise INPUT.error("proof-incomplete", f"close proof child {index} is not an object")
        INPUT.fields(child, {"repo", "number", "evidence"}, f"close proof child {index}")
        child_repo = INPUT.repo(child.get("repo"), f"close proof child {index}.repo")
        if child_repo.lower() != repo.lower():
            raise INPUT.error("parent-mismatch", f"close proof child {index} has a foreign repository")
        child_number = INPUT.positive(child.get("number"), f"close proof child {index}.number")
        child_key = (child_repo.lower(), child_number)
        if child_key in seen_children:
            raise INPUT.error("proof-incomplete", "close proof repeats a child identity")
        seen_children.add(child_key)
        evidence = child.get("evidence")
        if not isinstance(evidence, dict) or set(evidence) != {"kind", "identity"}:
            raise INPUT.error(
                "proof-incomplete", f"close proof child {index} needs issue-owned evidence identity"
            )
        if evidence.get("kind") != "issue-owned-closeout/v1":
            raise INPUT.error(
                "proof-incomplete", f"close proof child {index} has an unsupported evidence kind"
            )
        if not isinstance(evidence.get("identity"), str) or not evidence["identity"].strip():
            raise INPUT.error(
                "proof-incomplete", f"close proof child {index} evidence identity is empty"
            )
    return value


def _validate_fields(
    value: dict[str, Any], *, repo: str, parent_number: int
) -> list[dict[str, Any]]:
    INPUT.fields(
        value,
        {
            "kind", "repo", "parent_number", "attempt_id", "draft_sha256", "binding_sha256",
            "observation_dir", "comment_file", "classification", "reason", "manual_target_declaration",
            "children", "comment_sha256", "final_proof_index_file",
            "final_proof_index_sha256",
        },
        "close proof",
    )
    if INPUT.repo(value.get("repo"), "close proof.repo").lower() != repo.lower():
        raise INPUT.error("parent-mismatch", "close proof repository differs from the requested repository")
    if INPUT.positive(value.get("parent_number"), "close proof.parent_number") != parent_number:
        raise INPUT.error("parent-mismatch", "close proof parent differs from the requested parent")
    attempt_id = value.get("attempt_id")
    if not isinstance(attempt_id, str) or not INPUT.ATTEMPT_RE.fullmatch(attempt_id):
        raise INPUT.error("identity-invalid", "close proof.attempt_id has unsupported syntax")
    INPUT.sha(value.get("draft_sha256"), "close proof.draft_sha256")
    INPUT.sha(value.get("binding_sha256"), "close proof.binding_sha256")
    if not isinstance(value.get("observation_dir"), str) or not value["observation_dir"].strip():
        raise INPUT.error("path-invalid", "close proof.observation_dir must be non-empty text")
    if not isinstance(value.get("comment_file"), str) or not value["comment_file"].strip():
        raise INPUT.error("input-missing", "close proof requires comment_file")
    INPUT.sha(value.get("comment_sha256"), "close proof.comment_sha256")
    index_file = value.get("final_proof_index_file")
    if not isinstance(index_file, str) or not index_file.strip():
        raise INPUT.error("input-missing", "close proof requires final_proof_index_file")
    INPUT.sha(value.get("final_proof_index_sha256"), "close proof.final_proof_index_sha256")
    return _validate_children(value.get("children"), repo=repo)


def _validate_bound_inputs(
    value: dict[str, Any],
    result: dict[str, Any],
    *,
    repo_root: Path,
    repo: str,
    parent_number: int,
    children: list[dict[str, Any]],
) -> None:
    root = repo_root.resolve()
    proof_path = INPUT.repo_file(root, result["path"], context="proof_file")
    if proof_path != Path(result["path"]).resolve():
        raise INPUT.error("path-invalid", "close proof must be contained by the repository root")
    comment_path = INPUT.repo_file(root, value["comment_file"], context="close proof comment_file")
    try:
        comment_path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise INPUT.error("input-invalid", "close proof comment_file is not valid UTF-8 text") from exc
    comment_digest = hashlib.sha256(comment_path.read_bytes()).hexdigest()
    if comment_digest != value["comment_sha256"]:
        raise INPUT.error(
            "input-stale",
            "close proof comment bytes do not match its declared SHA-256: "
            f"expected {value['comment_sha256']}, got {comment_digest}",
        )
    observation_dir = INPUT.repo_file(
        root, value["observation_dir"], context="close proof observation_dir", must_exist=False
    )
    if observation_dir.exists() and not observation_dir.is_dir():
        raise INPUT.error("path-invalid", "close proof observation_dir must name a directory")
    index_path = INPUT.repo_file(
        root, value["final_proof_index_file"], context="close proof final_proof_index_file"
    )
    final_index = load_final_proof_index(
        index_path,
        repo_root=root,
        repo=repo,
        parent_number=parent_number,
        draft_sha256=value["draft_sha256"],
        binding_sha256=value["binding_sha256"],
        sha256=value["final_proof_index_sha256"],
    )
    proof_children = sorted(
        ({"repo": child["repo"], "number": child["number"]} for child in children),
        key=lambda child: (child["repo"].lower(), child["number"]),
    )
    expected_children = sorted(
        final_index["expected_children"],
        key=lambda child: (child["repo"].lower(), child["number"]),
    )
    if proof_children != expected_children:
        raise INPUT.error(
            "evidence-mismatch",
            "close proof children do not match the separately bound final proof index",
        )
    result.update(
        comment_path=str(comment_path),
        observation_dir_path=str(observation_dir),
        final_proof_index=final_index,
    )


def load_close_proof(
    path: Path,
    *,
    repo: str,
    parent_number: int,
    repo_root: Path | None = None,
) -> dict[str, Any]:
    value, digest = INPUT.read_json(path, kind=CLOSE_PROOF_KIND)
    children = _validate_fields(value, repo=repo, parent_number=parent_number)
    result: dict[str, Any] = {**value, "path": str(path), "sha256": digest}
    if repo_root is not None:
        _validate_bound_inputs(
            value,
            result,
            repo_root=repo_root,
            repo=repo,
            parent_number=parent_number,
            children=children,
        )
    return result
